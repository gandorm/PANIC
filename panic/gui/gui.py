import sys, re, os, traceback, time
import threading, Queue

import fandango as fn
import fandango.tango as ft
import fandango.qt

from fandango.functional import *
from fandango.qt import Qt
from fandango.excepts import Catched
from fandango.objects import Cached
from fandango.log import tracer,shortstr

import panic
import panic.view

import taurus
import taurus.qt.qtgui.base
from taurus.qt.qtgui import container
from taurus.qt.qtgui.panel import TaurusForm

try:
  from taurus.core.tango.tangovalidator import \
      TangoAttributeNameValidator as AttributeNameValidator
except:
  #Taurus3
  from taurus.core import AttributeNameValidator

#from row import AlarmRow, QAlarm, QAlarmManager
from panic.gui.actions import QAlarmManager
from panic.gui.views import ViewChooser
from panic.gui.utils import * #< getThemeIcon, getIconForAlarm imported here
from panic.gui.utils import WindowManager #Order of imports matters!
from panic.gui.editor import FormulaEditor,AlarmForm
from panic.gui.core import Ui_AlarmList
from panic.gui.alarmhistory import *

PANIC_URL = 'http://www.pythonhosted.org/panic'    

HELP = """
Usage:
    > panic [-?/--help] [-v/--attach] f0 f1 f2 [--scope=...] [--default=...]

Without arguments, it will parse defaults from 
PANIC.DefaultArgs property of Tango Database

--scope will constrain the devices accessed by the application, cannot
be changed on runtime.

--default will setup a default regular expression to be applied when 
the search field is empty. It will be overriden by any expression entered
by user

Filters (f0, f1, ...) just initialize the regular expression 
search to a default value.



"""

OPEN_WINDOWS = []

import utils as widgets
widgets.TRACE_LEVEL = 1 #-1

    ###########################################################################
    
PARENT_CLASS = Qt.QWidget
class QAlarmList(QAlarmManager,iValidatedWidget,PARENT_CLASS):
    """    
    Class for managing the self updating alarm list in AlarmGUI.
    
    Arguments and options explained in gui.HELP and AlarmGUI classes
    
    This is just the graphical part,  update/sorting algorithm 
    is implemented by panic.AlarmView class 
    """
    
    #Default period between list order updates
    REFRESH_TIME = 3000
    #Default period between database reloads
    RELOAD_TIME = 60000 
    # new refresh set by hurry()
    MAX_REFRESH = 500 
    #AlarmRow.use_list will be enabled only if number of alarms > MAX_ALARMS
    MAX_ALARMS = 30 
    #Controls if alarm events will hurry buildList()
    USE_EVENT_REFRESH = False 
    
    ALARM_ROW = ['tag','get_state','get_time','device','description']
    ALARM_LENGTHS = [50,10,20,25,200]
    
    __pyqtSignals__ = ("valueChanged",)
    
    def __init__(self, parent=None, filters='', options=None, mainwindow=None):
              
        options = options or {}
        if not fn.isDictionary(options):
            options = dict((o.replace('-','').split('=')[0],o.split('=',1)[-1]) 
                for o in options)
            
        trace( 'In AlarmGUI(%s): %s'%(filters,options))

        self.last_reload = 0
        self.AlarmRows = {}
        self.timeSortingEnabled=None
        self.changed = True
        self.severities = [] #List to keep severities currently visible
        
        self.expert = False
        self.tools = {} #Widgets dictionary
        
        self.scope = options.get('scope','*') #filters or '*'
        self.default_regEx = options.get('default',filters or '*')
        self.regEx = self.default_regEx
        self.init_ui(parent,mainwindow) #init_mw is called here
        self.NO_ICON = Qt.QIcon()
        
        refresh = int(options.get('refresh',self.REFRESH_TIME))
        self.REFRESH_TIME = refresh
         #AlarmRow.REFRESH_TIME = refresh
        
        #if self.regEx not in ('','*'): 
            #print 'Setting RegExp filter: %s'%self.regEx
            #self._ui.regExLine.setText(str(self.regEx))
               
        self.api = panic.AlarmAPI(self.scope)
        trace('AlarmGUI(%s): api done'%self.scope)

        # @TODO: api-based views are not multi-host
        self.view = panic.view.AlarmView(api=self.api,scope=self.scope,
                refresh = self.REFRESH_TIME/1e3,events=False,verbose=1) 
        trace('AlarmGUI(): view done')
        
        self.snapi = None
        self.ctx_names = []

        if not self.api.keys(): trace('NO ALARMS FOUND IN DATABASE!?!?')
        #AlarmRow.TAG_SIZE = 1+max([len(k) for k in self.api] or [40])
        
        N = len(self.getAlarms())
        trace('AlarmGUI(): %d alarms'%N)
        if N<150: 
            self._ui.sevDebugCheckBox.setChecked(True)
            self._ui.activeCheckBox.setChecked(False)
        else:
            self._ui.sevDebugCheckBox.setChecked(False)
            self._ui.activeCheckBox.setChecked(True)
            
        if N<=self.MAX_ALARMS: self.USE_EVENT_REFRESH = True
        

        self.init_timers()
        self.init_filters()        
        
        trace('AlarmGUI(): signals done')
        ## connection of ui signals is delayed until first onRefresh()
        
        self.updateStatusLabel()
                    
        trace('AlarmGUI(): done')
        
        ## TODO: in case of "Dead" Panic devices a message should be shown
        # here
    
    ###########################################################################
        
    @Cached(expire=0.2)
    def getAlarms(self):
        """
        It returns a list with all alarms matching the default View filter
        @TODO: it should ignore the current filters set by user.
        """
        trace('getAlarms(): sorting ...',level=0)
        self.view.sort()
        return self.view.ordered
    
    @Cached(expire=0.2)
    def getCurrents(self):
        """
        It returns only the currently shown alarms matching user filters
        """
        return self.getAlarms() #_ordered
    
    def setModel(self,model):
        """
        Method called when a model is set externally (synoptic of drop event)
        """
        # THIS METHOD WILL CHECK FOR CHANGES IN FILTERS (not only severities)
        try:
            if model!= self.regEx:
                print('AlarmGUI.setModel(%s)'%model)
                self._ui.regExLine.setText(model or self.default_regEx)
                self.onRegExUpdate()
        except:
            print traceback.format_exc()

    ###########################################################################
    # AlarmList
    
    def emitValueChanged(self):
        #trace ('emitValueChanged()')
        self.emit(Qt.SIGNAL("valueChanged"))    
    
    def init_timers(self):
        #TIMERS (to reload database and refresh alarm list).
        self.reloadTimer = Qt.QTimer()
        self.refreshTimer = Qt.QTimer()
        Qt.QObject.connect(self.refreshTimer, 
                           Qt.SIGNAL("timeout()"), self.onRefresh)
        Qt.QObject.connect(self.reloadTimer, 
                           Qt.SIGNAL("timeout()"), self.onReload)
        #first fast loading
        self.reloadTimer.start(min((5000,self.REFRESH_TIME/2.))) 
        self.refreshTimer.start(self.REFRESH_TIME)    
        
    def hurry(self):
        """
        on ValueChanged event a refresh will be scheduled in 1 second time
        (so all events received in a single second will be summarized)
        """
        if not self.changed: 
            trace('hurry(), changed = True')
            self.changed = True
            self.reloadTimer.setInterval(self.MAX_REFRESH)

    @Catched
    def onReload(self):
        # THIS METHOD WILL NOT MODIFY THE LIST IF JUST FILTERS HAS CHANGED; 
        # TO UPDATE FILTERS USE onRefresh INSTEAD
        try:
            trace('onReload(%s)'%self.RELOAD_TIME)
            print '+'*80
            now = time.time()
            trace('%s -> AlarmGUI.onReload() after %f seconds'%(
              now,now-self.last_reload))
            self.last_reload=now
            self.api.load()
            #self.checkAlarmRows()
                    
            #Updating the alarm list
            self.buildList(changed=False)
            if self.changed: self.showList()
            
            #Triggering refresh timers
            self.reloadTimer.setInterval(self.RELOAD_TIME)
            self.refreshTimer.setInterval(self.REFRESH_TIME)

            if not self._connected:
                self._connected = True
                self.connectAll()
        except:
            trace(traceback.format_exc())
    
    @Catched
    def onRefresh(self):
        """Just checks order, no reload, no filters"""
        trace('onRefresh(%s)'%self.REFRESH_TIME,level=1)
        self.buildList(changed=False)
        #if self.changed: ## Changed to be computed row by row
        self.showList()
        self.refreshTimer.setInterval(self.REFRESH_TIME)
        
    def updateStatusLabel(self):
        #nones = len([v for v in self.AlarmRows.values() if v.alarm is None])
        alarms = self.getCurrents()
        size = len(self.api)
        nones = len([v for v in alarms if not v.updated])
        added = len(alarms) #self._ui.listWidget.count()
        
        if nones or not self._connected: 
            text = 'Loading %s ... %d / %d'%(
              self.scope,size-nones,size)
        else: 
            text = (time2str()+': Showing %d %s alarms,'
              ' %d in database.'%(added,self.scope,size))

        trace(text+', nones = %d'%nones)
        self._ui.statusLabel.setText(text)
        if not nones and self.splash:
            try: 
                print 'closing splash ...'
                self.splash.finish(None)
                self.splash = None
            except: print traceback.format_exc()          
            
        return
      

    ###########################################################################
    # AlarmActions
    
    def onItemSelected(self):
        try:
            items = self.getSelectedRows(extend=False)
            if len(items)==1:
                a = self.view.get_alarm_from_text(items[0])
                tags = a.tag.split('_')
                self.emit(Qt.SIGNAL('alarmSelected'),a.tag)
                models = self.api.parse_attributes(a.formula)
                devices = sorted(set(fn.tango.parse_tango_model(m)['device'] 
                                     for m in models))
                print 'onItemSelected(%s): %s'%(a,devices)
                self.emit(Qt.SIGNAL('devicesSelected'),'|'.join(devices+tags))
        except: traceback.print_exc()      
            
    def getCurrentAlarm(self,item=None):
        tag = self.getCurrentTag(item)
        return self.api[tag]
    
    def getCurrentTag(self,item=None):
        row = item or self._ui.listWidget.currentItem()
        return self.view.get_alarm_from_text(row.text())
      
    def onSelectAllNone(self):
        if self._ui.selectCheckBox.isChecked():
            self._ui.listWidget.selectAll()
        else:
            self._ui.listWidget.clearSelection()
        
    def getSelectedRows(self,extend=False):
        """
        extend=True will add children alarms, be careful
        """
        targets = self._ui.listWidget.selectedItems()
        if extend:
            subs = [a for t in targets 
                    for a in self.api.parse_alarms(t.alarm.formula)]
            targets.extend(self.AlarmRows.get(a) 
                    for a in subs if a in self.AlarmRows and not any(t.tag==a for t in targets))
        return targets
    
    def getSelectedAlarms(self):
        rows = self.getSelectedRows()
        return [self.getCurrentAlarm(r) for r in rows]
      
    def getVisibleRows(self,margin=10):
        ql = self._ui.listWidget
        rows = [i for i in range(ql.count()) if 
                ql.visibleRegion().contains(
                  ql.visualItemRect(ql.item(i)))]
        if rows:
            rows = range(max((0,rows[0]-margin)),
                  min((ql.count(),rows[-1]+margin)))
        return rows
      
    def setScrollHook(self,hook):
        """ Hook must be a callable with an int as argument"""
        self._ui.listWidget.verticalScrollBar.valueChanged.connect(hook)
        
    @staticmethod
    def setFontsAndColors(item,alarm):
      
        state,severity = alarm.get_state(),alarm.severity
        severity = severity or panic.DEFAULT_SEVERITY
        color = Qt.QColor("black")
        background = Qt.QColor("white")
        bold = False
        icon = ""
        
        if state in ('OOSRV',):
            color = Qt.QColor("grey").light()
            background = Qt.QColor("white")
            
        elif state in ('ERROR',):
            color = Qt.QColor("red")
            background = Qt.QColor("white")
            
        elif state in ('ACKED','ACTIVE','RTNUN'):
            
            if severity in ('ERROR',):
                color = Qt.QColor("white")
                background = Qt.QColor("red").lighter()            

            elif severity in ('ALARM',):
                background = Qt.QColor("red").lighter()
                
            elif severity == 'WARNING':
                background = Qt.QColor("orange").lighter()
                
            elif severity in ('INFO','DEBUG'):
                background = Qt.QColor("yellow").lighter()
                
        elif state in ('DSUPR','SHLVD'):
            color = Qt.QColor("grey").light()
            background = Qt.QColor("white")
            
        elif state == 'NORM':
            color = Qt.QColor("green").lighter()
            background = Qt.QColor("white")
            
        else:
            raise Exception('UnknownState:%s'%state)
          
        icon = getIconForAlarm(alarm)
            
        if (fandango.now() - alarm.get_time()) < 60:
            bold = True

        alarmicon=getThemeIcon(icon) if icon else None
        tracer('setFontsAndColors(%s,%s,%s,%s,%s)'
          %(alarm.tag,state,icon,background,bold))
        item.setIcon(alarmicon or Qt.QIcon())
        item.setTextColor(color)
        item.setBackgroundColor(background)
        f = item.font()
        f.setFixedPitch(True)
        f.setBold(bold)
        item.setFont(f)
        
        status = [
            'Severity: '+alarm.severity,
            'Formula: '+alarm.formula,
            'Description: %s'%alarm.description,
            'Alarm Device: %s'%alarm.device,
            'Archived: %s'%('Yes' if 'SNAP' in alarm.receivers else 'No'),
            ]
        for t in ('last_error','acknowledged','disabled','sortkey'):
            v = getattr(alarm,t,None)
            if v: status.append('%s%s: %s'%(t[0].upper(),t[1:],shortstr(v)))
            
        item.setToolTip('\n'.join(status))
        
        try:
            forms = []
            for f in WindowManager.WINDOWS:
                if isinstance(f,AlarmForm):
                    tag = f.getCurrentAlarm().tag
                    if tag == alarm.tag:
                        forms.append(f)
            if forms:
                #@TODO: these checks will be not needed after full update
                alarm.get_enabled(force=True)
                alarm.get_acknowledged(force=True)
                tracer("\tupdating %d %s forms"%(len(forms),alarm))
                [f.valueChanged() for f in forms]
            else:
                tracer("no forms open?")
        except:
            tracer(traceback.format_exc())
                
        return item

    @Catched
    def buildList(self,changed=False,block=False):
        if block: self._ui.listWidget.blockSignals(True)
        
        self.changed = changed or self.changed
        trace('buildList(%s)'%self.changed,level=2)

        try:
            self.view.apply_filters(**self.getFilters())     
        except:
            trace('AlarmGUI.buildList(): Failed!\n%s'%traceback.format_exc())
            
        #if not self.changed: print '\tAlarm list not changed'
        if block: self._ui.listWidget.blockSignals(False)

    @Catched
    def showList(self,delete=False):
        """
        This method just redraws the list keeping the currently selected items
        """
        trace('%s -> AlarmGUI.showList()'%time.ctime(),level=2)
        #self._ui.listWidget.blockSignals(True)
        currents,news = [a.tag for a in self.getSelectedAlarms()],[]
        trace('\t\t%d items selected'%len(currents),level=3)
        
        if delete:
            trace('\t\tremoving objects from the list ...')
            while self._ui.listWidget.count():
                delItem = self._ui.listWidget.takeItem(0)
                #del delItem
            
        trace('\t\tdisplaying the list ...',level=2)
        ActiveCheck = self._ui.activeCheckBox.isChecked() \
                        or self.timeSortingEnabled
        
        data = self.view.sort()
        
        if not data:
            trace('NO ALARMS FOUND!!!',level=1)
        else:
            self.ALARM_LENGTHS[0] = max(len(str(t).split('/')[-1]) 
                                        for t in data)
            self.ALARM_LENGTHS[3] = max(len(str(t).rsplit('/',1)[0]) 
                                        for t in data)
            
        for i in range(len(data)): #self.getVisibleRows():
            t = data[i]
            try:
                data[i] = (self.view.get_alarm(t),
                           self.view.get_alarm_as_text(t,
                              cols=self.ALARM_ROW,
                              lengths=self.ALARM_LENGTHS))
            except:
                traceback.print_exc()

        # data is now a sorted list of alarm,text rows
        for i,t in enumerate(data): #self._ordered:
            #obj = self.AlarmRows[alarm.tag]
            #if not ActiveCheck or (obj.alarm and not obj.alarmAcknowledged 
                                   #and (obj.alarm.active 
                                  #or (not self.timeSortingEnabled 
                                  #and str(obj.quality) == 'ATTR_INVALID'))):
            alarm,text = t
            if i>=self._ui.listWidget.count():
                self._ui.listWidget.addItem("...")
                font = Qt.QFont(Qt.QString("Courier"))
                self._ui.listWidget.item(i).setFont(font)
            
            item = self._ui.listWidget.item(i)
            row = str(item.text())
            if text!=row:
                #font = Qt.QFont(Qt.QString("Courier"))
                #self._ui.listWidget.item(i).setFont(font)
                item.setText(text)
                self.setFontsAndColors(item,alarm)

            if alarm.tag in currents:
                try:
                    trace('\tselect %s'%alarm.tag)
                    item.setSelected(True)
                    if alarm.tag == currents[0]:
                        self._ui.listWidget.setCurrentItem(item)
                except: traceback.print_exc()
            else:
                item.setSelected(False)
            
        for i in range(len(data),self._ui.listWidget.count()):
            item = self._ui.listWidget.item(i)
            item.setText('')
            item.setBackgroundColor(Qt.QColor('white'))
            item.setIcon(self.NO_ICON)
            
        self.changed = False
        trace('\t\tshowList(): %d alarms match filters.'
              %self._ui.listWidget.count())
        self.updateStatusLabel() #< getAlarms() called again here
        
        #self._ui.listWidget.blockSignals(False)
        
      
    ###########################################################################
    
class QFilterGUI(QAlarmList):
    """
    Class for managing the multiple filter widgets in AlarmGUI
    
    Arguments and options explained in gui.HELP and AlarmGUI classes
    """    
  
    def init_filters(self):
        trace('Setting combos ...')
        self.source = "" #Value in first comboBox
        self.setFirstCombo()
        self.setSecondCombo()
        self._ui.infoLabel0_1.setText(self._ui.contextComboBox.currentText())
        Qt.QObject.connect(self._ui.contextComboBox, 
                           Qt.SIGNAL("currentIndexChanged(QString)"), 
                           self._ui.infoLabel0_1.setText)
        Qt.QObject.connect(self._ui.contextComboBox, 
                           Qt.SIGNAL("currentIndexChanged(int)"), 
                           self.setSecondCombo)
        Qt.QObject.connect(self._ui.comboBoxx, 
                           Qt.SIGNAL("currentIndexChanged(QString)"), 
                           self.onFilter)
        
        Qt.QObject.connect(self._ui.regExUpdate, 
                           Qt.SIGNAL("clicked(bool)"), self.onRegExUpdate)
        Qt.QObject.connect(self._ui.selectCheckBox, 
                           Qt.SIGNAL('stateChanged(int)'), self.onSelectAllNone)
        Qt.QObject.connect(self._ui.activeCheckBox, 
                           Qt.SIGNAL('stateChanged(int)'), self.onFilter)
        Qt.QObject.connect(self._ui.sevAlarmCheckBox, 
                           Qt.SIGNAL('stateChanged(int)'), self.onSevFilter)
        Qt.QObject.connect(self._ui.sevErrorCheckBox, 
                           Qt.SIGNAL('stateChanged(int)'), self.onSevFilter)
        Qt.QObject.connect(self._ui.sevWarningCheckBox, 
                           Qt.SIGNAL('stateChanged(int)'), self.onSevFilter)
        Qt.QObject.connect(self._ui.sevDebugCheckBox, 
                           Qt.SIGNAL('stateChanged(int)'), self.onSevFilter)  
        
    def getFilters(self):
        #@TODO: Only regexp filter implemented
        trace("%s -> AlarmGUI.getFilters(%s)"%(time.ctime(), ['%s=%s'%(
            s,getattr(self,s,None)) for s in 
            ('regEx','severities','timeSortingEnabled','changed',)]),level=2)
        
        tag = device = receiver = formula = ''
        regexp = str(self.regEx).lower().strip().replace(' ','*')
        
        active = self._ui.activeCheckBox.isChecked() \
                        or self.timeSortingEnabled
                    
        combo1 = str(self._ui.contextComboBox.currentText())
        combo2 = str(self._ui.comboBoxx.currentText()).strip()
        if combo1 == 'Alarm': 
            #@TODO: To be replaced by state: ANY/NORM/ALARM/....
            pass        
        elif combo1 == 'Time':
            time_sorting = True
        elif combo1 == 'Devices': 
            device = combo2
        elif combo1 == 'Hierarchy': 
            pass
        elif combo1 == 'Receiver':
            receiver = combo2
        #elif combo1 == 'Severity': 
            #pass
        
        if regexp and not clmatch('^[~\!\*].*',regexp): 
            regexp = '*'+regexp+'*'
            
        regexp = regexp or self.default_regEx
        dct = {'tag':regexp or self.default_regEx}
        #if not any(device,r
        dct = {'tag':tag or regexp,
                'device':device or regexp,
                'receiver':receiver or regexp,
                'formula':regexp,
                'active':active,
                }
        return dct
        
    
    def setFirstCombo(self):
        self.setComboBox(self._ui.contextComboBox,
                         ['Alarm','Time','Devices',
                        'Hierarchy','Receiver','Severity'],sort=False)

    def setSecondCombo(self):
        source = str(self._ui.contextComboBox.currentText())
        trace("AlarmGUI.setSecondCombo(%s)"%source)
        if source == self.source: return
        else: self.source = source
        self._ui.comboBoxx.clear()
        self._ui.comboBoxx.show()
        self._ui.infoLabel0_1.show()
        self._ui.comboBoxx.setEnabled(True)
        if source =='Devices':
            r,sort,values = 1,True,sorted(set(a.device 
                                              for a in self.getAlarms()))
        elif source =='Receiver':
            #r,sort,values = 2,True,list(set(a for a in self.api.phonebook.keys() for l in self.api.values() if a in l.receivers))
            r,sort,values = 2,True,list(set(s for a in self.getAlarms() for s in ['SNAP','SMS']+[r.strip() for r in a.receivers.split(',')]))
        elif source =='Severity':
            r,sort,values = 3,False,['DEBUG', 'WARNING', 'ALARM', 'ERROR']
        elif source =='Hierarchy':
            r,sort,values = 4,False,['ALL', 'TOP', 'BOTTOM']
        elif source =='Time':
            r,sort,values = 5,False,['DESC', 'ASC']
        else: #"Alarm Status"
            r,sort,values = 0,False,['ALL', 'AVAILABLE', 'FAILED','HISTORY']
        self.setComboBox(self._ui.comboBoxx,values=values,sort=sort)
        return r

    def setComboBox(self, comboBox, values, sort=False):
#        print "setRecData"
        comboBox.clear()
        [comboBox.addItem(Qt.QString(i)) for i in values]
        if sort: comboBox.model().sort(0, Qt.Qt.AscendingOrder)
        
    def setSeverity(self,tag,severity):
        tags = tag if fn.isSequence(tag) else [tag]
        self.setAllowedUsers(self.api.get_admins_for_alarm(len(tags)==1 and tags[0]))
        if not self.validate('setSeverity(%s,%s)'%(tags,severity)):
            return
        for tag in tags:
            severity = str(severity).upper().strip()
            if severity not in panic.SEVERITIES: raise Exception(severity)
            self.AlarmRows[tag].get_alarm_object().setup(severity=severity.upper(),write=True)
        [f.setAlarmData() for f in WindowManager.WINDOWS if isinstance(f,AlarmForm)]
        
    def getSeverities(self):
        self.severities=[]
        if self._ui.sevAlarmCheckBox.isChecked(): self.severities.append('alarm')
        if self._ui.sevErrorCheckBox.isChecked(): self.severities.append('error')
        if self._ui.sevWarningCheckBox.isChecked():
            self.severities.append('warning')
            self.severities.append('')
        if self._ui.sevDebugCheckBox.isChecked(): self.severities.append('debug')
        return self.severities
      
    ###########################################################################
    
    @Catched
    def onFilter(self,*args):
        """Forces an update of alarm list order and applies filters 
        (do not reload database)."""
        trace('onFilter()')
        self.buildList(changed=True)
        self.showList()
        self.refreshTimer.setInterval(self.REFRESH_TIME)

    def onSevFilter(self):
        # THIS METHOD WILL CHECK FOR CHANGES IN FILTERS (not only severities)
        self.getSeverities()
        self.onFilter()

    def onRegExUpdate(self):
        # THIS METHOD WILL CHECK FOR CHANGES IN FILTERS (not only severities)
        self.regEx = (str(self._ui.regExLine.text()).strip() 
            or self.default_regEx)
        #self._ui.activeCheckBox.setChecked(False)
        self.onFilter()

    @Catched
    def regExFiltering(self, source):
        msg = 'regExFiltering DEPRECATED by AlarmView'
        print(msg)
        raise Exception(msg)
        alarms,regexp=[],str(self.regEx).lower().strip().replace(' ','*')
        exclude = regexp.startswith('!') or regexp.startswith('~')
        if exclude: regexp = regexp.replace('!','').replace('~').strip()
        for a in source:
            match = fn.searchCl(regexp, a.receivers.lower()+' '
                        +a.severity.lower()+' '+a.description.lower()
                        +' '+a.tag.lower()+' '+a.formula.lower()+' '
                        +a.device.lower())
            if (exclude and not match) or (not exclude and match): 
                alarms.append(a)
        trace('\tregExFiltering(%d): %d alarms returned'
              %(len(source),len(alarms)))
        return alarms    

    ###########################################################################      
    
class AlarmGUI(QFilterGUI):
    """
    AlarmGUI, to generate Main window menus and parse OS arguments.

    GUI behaviour is implemented in QFilterGUI and QAlarmList classes.
    
    To see accepted OS arguments run: 

        #python panic/gui/gui.py --help
        
    Summarized:
        
    - PANIC_DEFAULT is a default view, overriden by --view
    - .scope and .default may be defined in the view, and later overriden by arguments
    - --scope="*regexp*" would be the filter to be passed to the panic.api: gui.scope
    - --scope=url1,url2,url3 would be used to open multiple api's
    - --default="*regexp*" would be the default filter for the search bar: gui.default
    - whenever the search bar is empty, .default is used instead
    - args will be joined as gui default
    - gui.current_search: the current contents of the search bar (gui.regEx)
    - gui.current_view: the currently selected view (?)        
    
        
    """
       
    def init_ui(self,parent,mainwindow):
        
        try:
            PARENT_CLASS.__init__(self,parent)
            self._connected = False
            self._ui = Ui_AlarmList()
            self._ui.setupUi(self)
            if mainwindow:
                mainwindow = self.init_mw(mainwindow)
            self.mainwindow = mainwindow
            
            url = os.path.dirname(panic.__file__)+'/gui/icon/panic-6-banner.png'
            trace('... splash ...')
            px = Qt.QPixmap(url)
            self.splash = Qt.QSplashScreen(px)
            self.splash.showMessage('initializing application...')
            self.splash.show()
            trace('showing splash ... %s'%px.size())
            
        except: 
            print traceback.format_exc()
            
        if self.mainwindow:
            
            self.mainwindow.setWindowTitle('PANIC (%s[%s]@%s)'%(
                self.scope,self.default_regEx,
                fn.get_tango_host().split(':')[0]))
            
            icon = '/gui/icon/panic-6-big.png' #'.svg'
            url = os.path.dirname(panic.__file__)+icon
            px = Qt.QPixmap(url)
            self.mainwindow.setWindowIcon(Qt.QIcon(px))
            
        self.setExpertView(True)

        self._message = Qt.QMessageBox(self)
        self._message.setWindowTitle("Empty fields")
        self._message.setIcon(Qt.QMessageBox.Critical)
        
    def connectAll(self):
        trace('connecting')
        
        #Qt.QObject.connect(self.refreshTimer, Qt.SIGNAL("timeout()"), self.onRefresh)
        if self.USE_EVENT_REFRESH: 
            Qt.QObject.connect(self,Qt.SIGNAL("valueChanged"),self.hurry)
        #Qt.QObject.connect(self, 
            #Qt.SIGNAL('setfontsandcolors'),AlarmRow.setFontsAndColors)
        Qt.QObject.connect(self._ui.listWidget, 
            Qt.SIGNAL("itemSelectionChanged()"), self.onItemSelected)
        Qt.QObject.connect(self._ui.listWidget, 
            Qt.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.onView) #self.onEdit)
        #Qt.QObject.connect(self._ui.listWidget, Qt.SIGNAL("currentRowChanged(int)"), self.setAlarmData)
        Qt.QObject.connect(self._ui.listWidget, 
            Qt.SIGNAL('customContextMenuRequested(const QPoint&)'), 
            self.onContextMenu)
        
        #Qt.QObject.connect(self._ui.actionExpert,
                            #Qt.SIGNAL("changed()"),self.setExpertView)
        Qt.QObject.connect(self._ui.newButton, 
                           Qt.SIGNAL("clicked()"), self.onNew) # "New"
        Qt.QObject.connect(self._ui.deleteButton, 
                           Qt.SIGNAL("clicked(bool)"), self.onDelete) # Delete
        Qt.QObject.connect(self._ui.refreshButton, 
                           Qt.SIGNAL("clicked()"), self.onReload) # "Refresh"        
        Qt.QObject.connect(self._ui.buttonClose,
                           Qt.SIGNAL("clicked()"), self.close)

        trace('all connected')
        
    def init_mw(self,tmw = None):    
        """ 
        Method to initialize main window (menus and frames) 
        """
        t0 = time.time()
        alarmApp = self
        tmw = tmw if isinstance(tmw,Qt.QMainWindow) else CleanMainWindow()
        tmw.setWindowTitle('PANIC')
        tmw.menuBar = Qt.QMenuBar(tmw)
        tmw.toolsMenu = Qt.QMenu('Tools',tmw.menuBar)
        tmw.fileMenu = Qt.QMenu('File',tmw.menuBar)
        tmw.viewMenu = Qt.QMenu('View',tmw.menuBar)
        tmw.helpMenu = Qt.QMenu('Help',tmw.menuBar)

        tmw.setMenuBar(tmw.menuBar)
        [tmw.menuBar.addAction(a.menuAction()) 
                for a in (tmw.fileMenu,tmw.toolsMenu,tmw.helpMenu,tmw.viewMenu)]
        toolbar = Qt.QToolBar(tmw)
        toolbar.setIconSize(Qt.QSize(20,20))
        
        tmw.helpMenu.addAction(getThemeIcon("applications-system"),
            "Webpage",lambda : os.system('konqueror %s &'%PANIC_URL))
        tmw.toolsMenu.addAction(getThemeIcon("applications-system"),
            "Jive",lambda : os.system('jive &'))
        tmw.toolsMenu.addAction(getThemeIcon("applications-system"),
            "Astor",lambda : os.system('astor &'))
        tmw.fileMenu.addAction(getThemeIcon(":/designer/back.png"),
            "Export to CSV file",alarmApp.saveToFile)
        tmw.fileMenu.addAction(getThemeIcon(":/designer/forward.png"),
            "Import from CSV file",alarmApp.loadFromFile)
        tmw.fileMenu.addAction(getThemeIcon(":/designer/filereader.png"),
            "Use external editor",alarmApp.editFile)
        tmw.fileMenu.addAction(getThemeIcon("applications-system"),
            "Exit",tmw.close)
        tmw.viewMenu.connect(tmw.viewMenu,
            Qt.SIGNAL('aboutToShow()'),alarmApp.setViewMenu)
        
        from phonebook import PhoneBook
        alarmApp.tools['bookApp'] = WindowManager.addWindow(
            PhoneBook(container=tmw))
        tmw.toolsMenu.addAction(getThemeIcon("x-office-address-book"), 
            "PhoneBook", alarmApp.tools['bookApp'].show)
        toolbar.addAction(getThemeIcon("x-office-address-book") ,
            "PhoneBook",alarmApp.tools['bookApp'].show)
        
        trend_action = (getThemeIcon(":/designer/qwtplot.png"),
            'Trend',
            lambda:WindowManager.addWindow(widgets.get_archive_trend(show=True))
            )
        tmw.toolsMenu.addAction(*trend_action)
        toolbar.addAction(*trend_action)
        
        alarmApp.tools['config'] = WindowManager.addWindow(
            widgets.dacWidget(container=tmw))
        tmw.toolsMenu.addAction(getThemeIcon("applications-system"),
            "Advanced Configuration", alarmApp.tools['config'].show)
        toolbar.addAction(getThemeIcon("applications-system") ,
            "Advanced Configuration",alarmApp.tools['config'].show)
        
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        tmw.addToolBar(toolbar)
        
        if SNAP_ALLOWED:
            alarmApp.tools['history'] = WindowManager.addWindow(
                widgets.ahWidget(container=tmw))
            tmw.toolsMenu.addAction(getThemeIcon("office-calendar"),
                "Alarm History Viewer",alarmApp.tools['history'].show)
            toolbar.addAction(getThemeIcon("office-calendar") ,
                "Alarm History Viewer",alarmApp.tools['history'].show)
        else:
            trace("Unable to load SNAP",'History Viewer Disabled!')
            
        alarm_preview_action = (getThemeIcon("accessories-calculator"),
            "Alarm Calculator",lambda g=alarmApp:WindowManager.addWindow(
                AlarmPreview.showEmptyAlarmPreview(g)))
            
        [o.addAction(*alarm_preview_action) for o in (tmw.toolsMenu,toolbar)]
        
        try:
            import PyTangoArchiving.widget.ArchivingBrowser
            MSW = PyTangoArchiving.widget.ArchivingBrowser.ModelSearchWidget
            alarmApp.tools['finder'] = WindowManager.addWindow(MSW())
            tmw.toolsMenu.addAction(getThemeIcon("system-search"),
                "Attribute Finder",alarmApp.tools['finder'].show)      
            toolbar.addAction(getThemeIcon("system-search"),
                "Attribute Finder",alarmApp.tools['finder'].show) 
        except:
            print('PyTangoArchiving not available')
            #traceback.print_exc()        
            
        print('Toolbars created after %s seconds'%(time.time()-t0))
        tmw.setCentralWidget(alarmApp)
        tmw.show()
        return tmw        
            
    ###########################################################################
    # GUI Main

    @staticmethod
    def main(args=[]):
        """Main launcher, load views and stops threads on exit"""
        
        t0 = time.time()
        args = args or ft.get_free_property('PANIC','DefaultArgs')    
        opts = [a for a in args if a.startswith('-')]
        args = [a for a in args if not a.startswith('-')] 
        
        if any(o in opts for o in ('-h','--help','-?')):
            print(HELP)
            return

        from taurus.qt.qtgui.application import TaurusApplication    
        uniqueapp = TaurusApplication([]) #opts)
        
        if '--calc' in opts:
            args = args or ['']
            form = AlarmPreview(*args)
            form.show()
            uniqueapp.exec_()
            return

        # ([os.getenv('PANIC_DEFAULT')] if os.getenv('PANIC_DEFAULT') else []))
        
        ## @TODO: Global views (multi-host) to be added
        #if not views:
            #vc = ViewChooser()
            #vc.exec_()
            #views = vc.view
        #if not views or not any(views):
            #sys.exit(-1)

        print '='*80
        trace('launching AlarmGUI ... %s, %s'%(args,opts))
        print '='*80
        alarmApp = AlarmGUI(filters='|'.join(args),
                            options=opts,mainwindow=True)
        print('AlarmGUI created after %s seconds'%(time.time()-t0))    
        #alarmApp.tmw.show()
        n = uniqueapp.exec_()

        print('AlarmGUI exits ...')    
        # Unsubscribing all event sources
        import fandango.threads
        import fandango.callbacks
        [s.unsubscribeEvents() for s 
            in fandango.callbacks.EventSource.get_thread().sources]
        fandango.threads.ThreadedObject.kill_all()
        sys.exit(n) 
        
    
    def close(self):
        print('AlarmGUI.close()')
        Qt.QApplication.quit()        
        
    ##########################################################################
    
    def printRows(self):
        for row in self._ui.listWidget.selectedItems():
          print row.__repr__()
    
    def saveToFile(self):
        filename = str(Qt.QFileDialog.getSaveFileName(
            self.mainwindow,'File to save','.','*.csv'))
        self.api.export_to_csv(filename,alarms=self.getCurrents())
        return filename
        
    def loadFromFile(self,default='*.csv',ask=True):
        try:
            errors = []
            if ask or '*' in default:
                if '/' in default: d,f = default.rsplit('/',1)
                else: d,f = '.',default
                filename = Qt.QFileDialog.getOpenFileName(self.mainwindow,
                                                          'Import file',d,f)
            else:
                filename = default
            if filename:
                if not self.validate('LoadFromFile(%s)'%filename): return
                alarms = self.api.load_from_csv(filename,write=False)
                selected = AlarmsSelector(sorted(alarms.keys()),
                                          text='Choose alarms to import')
                devs = set()
                for tag in selected:
                    v = alarms[tag]
                    if v['device'] not in self.api.devices: 
                        errors.append('%s does not exist!!!'%v['device'])
                    else:
                        devs.add(v['device'])
                        if tag not in self.api: self.api.add(**v)
                        else: self.api.modify(**v)
                [self.api.devices[d].init() for d in devs]
            if errors: 
                Qt.QMessageBox.warning(self.mainwindow,'Error',
                                       '\n'.join(errors),Qt.QMessageBox.Ok)
            return filename
        except:
            import traceback
            Qt.QMessageBox.warning(self.mainwindow,'Error',
                                   traceback.format_exc(),Qt.QMessageBox.Ok)
            
    def editFile(self):
        filename = self.saveToFile()
        editor,ok = Qt.QInputDialog.getText(self.mainwindow,
                    'Choose your editor',"Type your editor choice, "
                    "you'll have to call 'Import CSV' after editing",
                    Qt.QLineEdit.Normal,'oocalc %s'%filename)
        if ok:
            os.system('%s &'%str(editor))
            v = Qt.QMessageBox.warning(None,'Load from file', \
                    '%s file may have been modified, '
                    'do you want to load your changes?'%filename, \
                    Qt.QMessageBox.Yes|Qt.QMessageBox.No);
            if v == Qt.QMessageBox.Yes:
                self.loadFromFile(filename,ask=False)
            return filename
            
    def setViewMenu(self,action=None):
        print 'In AlarmGUI.setViewMenu(%s)'%action
        self.mainwindow.viewMenu.clear()
        windows = WindowManager.getWindowsNames()
        for w in windows:
            self.mainwindow.viewMenu.addAction(w,
                            lambda x=w:WindowManager.putOnTop(x))
        self.mainwindow.viewMenu.addAction('Close All',
                            lambda : WindowManager.closeAll())
        return
        
    def setExpertView(self,check=None):
        if check is None: check = self._ui.actionExpert.isChecked()
        self.expert = check
        self._ui.newButton.setEnabled(self.expert) #show()
        self._ui.deleteButton.setEnabled(self.expert) #show()
        self.expert = check
        return
    
    ###########################################################################
    
def main(args):
    AlarmGUI.main(args)
  
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

try:
    from fandango.doc import get_fn_autodoc
    __doc__ = get_fn_autodoc(__name__,vars())
except:
    #import traceback
    #traceback.print_exc()
    pass
