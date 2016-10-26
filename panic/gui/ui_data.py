from PyQt4 import QtCore, QtGui
from taurus.qt.qtgui.resource import getThemeIcon
from widgets import clickableQLineEdit, clickableQTextEdit

"""
ui_data.py, this file contains the Ui Classes used for AlarmEditor form.
"""

######################################################################################
class Ui_Data(object): 
    #Alarm Editor
    def setupUi(self, Data):
        self.Data=Data
        Data.setObjectName("Data")
        Data.resize(349, 275)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Data)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.nameLabel = QtGui.QLabel(Data)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setFont(self.font)
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 1)
        self.nameLineEdit = clickableQLineEdit(Data)
        self.nameLineEdit.setReadOnly(True)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLineEdit.setFont(self.font)
        self.gridLayout.addWidget(self.nameLineEdit, 0, 1, 1, 3)

        self.statusLabel = QtGui.QLabel(Data)
        self.statusLabel.setObjectName("statusLabel")
        self.gridLayout.addWidget(self.statusLabel, 1, 0, 1, 1)
        self.horizontalLane = QtGui.QHBoxLayout()
        self.horizontalLane.setObjectName("horizontalLayout")
        self.gridLayout.addLayout(self.horizontalLane, 1, 1, 1, 3)
        
        self.disableLabel = QtGui.QLabel(Data)
        self.disableLabel.setObjectName("disableLabel")
        self.gridLayout.addWidget(self.disableLabel, 2, 0, 1, 1)
        self.disabledCheckBox = QtGui.QCheckBox(Data)
        self.disabledCheckBox.setObjectName("disabledCheckBox")
        self.gridLayout.addWidget(self.disabledCheckBox, 2, 1, 1, 1)
        self.disabledCheckBox.setEnabled(False)
        self.ackLabel = QtGui.QLabel(Data)
        self.ackLabel.setObjectName("ackLabel")
        self.gridLayout.addWidget(self.ackLabel, 3, 0, 1, 1)
        self.ackCheckBox = QtGui.QCheckBox(Data)
        self.ackCheckBox.setObjectName("ackCheckBox")
        self.gridLayout.addWidget(self.ackCheckBox, 3, 1, 1, 1)
        self.ackCheckBox.setEnabled(False)


        self.deviceLabel = QtGui.QLabel(Data)
        self.deviceLabel.setObjectName("deviceLabel")
        self.gridLayout.addWidget(self.deviceLabel, 4, 0, 1, 1)
        self.deviceStackedLayout = QtGui.QStackedLayout()
        self.deviceStackedLayout.setObjectName("deviceStackedLayout")
        self.deviceCombo = QtGui.QComboBox(Data)
        self.deviceCombo.setObjectName("deviceCombo")
        self.deviceStackedLayout.addWidget(self.deviceCombo)
        self.deviceLineEdit = clickableQLineEdit(Data)
        self.deviceLineEdit.setReadOnly(True)
        self.deviceLineEdit.setObjectName("deviceLineEdit")
        self.deviceStackedLayout.addWidget(self.deviceLineEdit)
        self.deviceStackedLayout.setCurrentIndex(1)
        self.gridLayout.addLayout(self.deviceStackedLayout, 4, 1, 1, 2)
        
        self.deviceConfig = QtGui.QPushButton(Data)
        self.deviceConfig.setIcon(getThemeIcon("applications-system"))
        self.gridLayout.addWidget(self.deviceConfig, 4, 3, 1, 1)
        
        self.severityLabel = QtGui.QLabel(Data)
        self.severityLabel.setObjectName("severityLabel")
        self.gridLayout.addWidget(self.severityLabel, 5, 0, 1, 1)
        self.severityStackedLayout = QtGui.QStackedLayout()
        self.severityStackedLayout.setObjectName("severityStackedLayout")
        self.severityCombo=QtGui.QComboBox(Data)
        self.severityCombo.setObjectName("severityCombo")
        #self.severityCombo.connect(self.severityCombo,Q.textChanged,self.severityLineEdit.setText)
        self.severityStackedLayout.addWidget(self.severityCombo)
        self.severityLineEdit=clickableQLineEdit(Data)
        self.severityLineEdit.setReadOnly(True)
        self.severityLineEdit.setObjectName("severityLineEdit")
        self.severityStackedLayout.addWidget(self.severityLineEdit)
        self.severityStackedLayout.setCurrentIndex(1)
        self.gridLayout.addLayout(self.severityStackedLayout, 5, 1, 1, 3)

        self.descriptionLabel = QtGui.QLabel(Data)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.descriptionLabel.setMinimumWidth(70)
        self.gridLayout.addWidget(self.descriptionLabel, 6, 0, 1, 1)
        self.descriptionTextEdit = clickableQTextEdit(Data)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptionTextEdit.sizePolicy().hasHeightForWidth())
        self.descriptionTextEdit.setSizePolicy(sizePolicy)
        self.descriptionTextEdit.setMinimumSize(QtCore.QSize(0, 25))
        self.descriptionTextEdit.setReadOnly(True)
        self.descriptionTextEdit.setObjectName("descriptionTextEdit")
        self.gridLayout.addWidget(self.descriptionTextEdit, 6, 1, 1, 3)
        self.receiversLabel = QtGui.QLabel(Data)
        self.receiversLabel.setObjectName("receiversLabel")
        self.gridLayout.addWidget(self.receiversLabel, 7, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.receiversStackedLayout = QtGui.QStackedLayout()
        self.receiversStackedLayout.setObjectName("receiversStackedLayout")

        self.receiversLineEdit = clickableQLineEdit(Data)
        self.receiversLineEdit.setReadOnly(True)
        self.receiversLineEdit.setObjectName("receiversLineEdit")
        self.receiversLineEdit.setSizePolicy(sizePolicy)
        self.receiversStackedLayout.addWidget(self.receiversLineEdit)

        self.receiversWidget = QtGui.QWidget(Data)
        self.receiversWidget.setObjectName("receiversWidget")
#        self.receiversStackedLayout.addWidget(self.receiversWidget)
        self.receiversStackedLayout.setCurrentIndex(0)

        self.horizontalLayout.addLayout(self.receiversStackedLayout)
        self.addReceiversButton = QtGui.QPushButton(Data)
        self.addReceiversButton.setObjectName("addReceiversButton")
        self.addReceiversButton.setIcon(getThemeIcon("list-add"))
        self.horizontalLayout.addWidget(self.addReceiversButton)
        self.addReceiversButton.setEnabled(False)

        self.gridLayout.addLayout(self.horizontalLayout, 7, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        self.frame = QtGui.QFrame(Data)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.formulaStacked = QtGui.QStackedLayout(self.frame)
        self.formulaStacked.setObjectName("stackedLayout")

        self.formulaWidget = QtGui.QWidget(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.formulaWidget.sizePolicy().hasHeightForWidth())
        self.formulaWidget.setSizePolicy(sizePolicy)
        self.formulaWidget.setObjectName("formulaWidget")
        self.formulaStacked.addWidget(self.formulaWidget) # ad widget to stacked

        self.verticalLayout_2 = QtGui.QVBoxLayout(self.formulaWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.formulaLabel = QtGui.QLabel()#self.formulaWidget)
        #self.font = QtGui.QFont()
        #self.font.setPointSize(8)
        #self.font.setWeight(75)
        #self.font.setBold(True)
        #self.formulaLabel.setFont(self.font)
        #self.formulaLabel.setObjectName("formulaLabel")
        #self.verticalLayout_2.addWidget(self.formulaLabel)
        from widgets import AlarmFormula
        self.formulaTextEdit = AlarmFormula() #clickableQTextEdit(self.formulaWidget)
        self.formulaTextEdit.setReadOnly(True)
        self.formulaTextEdit.setObjectName("formulaTextEdit")
        self.verticalLayout_2.addWidget(self.formulaTextEdit)

        self.verticalLayout_3.addWidget(self.frame)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(self.spacerItem, 0, 2, 1, 1)
        self.editButton = QtGui.QPushButton(Data)
        self.font = QtGui.QFont()
        self.font.setPointSize(8)
        self.editButton.setFont(self.font)
        self.editButton.setObjectName("editButton")
        self.editButton.setIcon(getThemeIcon("accessories-text-editor"))
        self.gridLayout_2.addWidget(self.editButton, 0, 0, 1, 1)
        self.previewButton = QtGui.QPushButton(Data)
        self.font = QtGui.QFont()
        self.font.setPointSize(8)
        self.previewButton.setFont(self.font)
        self.previewButton.setObjectName("previewButton")
        self.previewButton.setIcon(getThemeIcon("face-glasses"))
        self.gridLayout_2.addWidget(self.previewButton, 0, 1, 1, 1)
        self.cancelButton = QtGui.QPushButton(Data)
        self.font = QtGui.QFont()
        self.font.setPointSize(8)
        self.cancelButton.setFont(self.font)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setIcon(getThemeIcon("edit-delete"))
        self.gridLayout_2.addWidget(self.cancelButton, 0, 4, 1, 1)
        self.saveButton = QtGui.QPushButton(Data)
        self.font = QtGui.QFont()
        self.font.setPointSize(8)
        self.saveButton.setFont(self.font)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setIcon(getThemeIcon("document-save"))
        self.gridLayout_2.addWidget(self.saveButton, 0, 3, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_2)

        self.retranslateUi(Data)
        QtCore.QMetaObject.connectSlotsByName(Data)

    def retranslateUi(self, Data):
        Data.setWindowTitle("Data")
        self.nameLabel.setText("Name:")
        self.statusLabel.setText('Status:')
        self.disableLabel.setText('Disabled:')
        self.ackLabel.setText('Acknowledged:')
        self.deviceLabel.setText("Device:")
        self.severityLabel.setText("Severity:")
        self.severityCombo.addItem('DEBUG')
        self.severityCombo.addItem('WARNING')
        self.severityCombo.addItem('ALARM')
        self.severityCombo.addItem('ERROR')

        self.descriptionLabel.setText("Description:")
        self.receiversLabel.setText("Receivers:")
        self.formulaLabel.setText("Formula:")
        self.editButton.setText("Edit")
        self.previewButton.setText("Preview")
        self.cancelButton.setText("Cancel")
        self.saveButton.setText("Save")

##########################################################################################################

class Ui_ReceiversLine(object):
    # Receivers Chooser
    def setupUi(self, ReceiversLine):
        self.ReceiversLine=ReceiversLine
        ReceiversLine.setObjectName("ReceiversLine")
        ReceiversLine.resize(303, 67)
        self.verticalLayout = QtGui.QVBoxLayout(ReceiversLine)
        self.verticalLayout.setObjectName("verticalLayout")
        self.receiversCombo = QtGui.QComboBox(ReceiversLine)
        self.receiversCombo.setObjectName("receiversCombo")
        self.verticalLayout.addWidget(self.receiversCombo)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.okButton = QtGui.QPushButton(ReceiversLine)
        self.okButton.setObjectName("okButton")
        self.gridLayout.addWidget(self.okButton, 0, 1, 1, 1)
        self.cancelButton = QtGui.QPushButton(ReceiversLine)
        self.cancelButton.setObjectName("cancelButton")
        self.gridLayout.addWidget(self.cancelButton, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(ReceiversLine)
        QtCore.QObject.connect(self.okButton, QtCore.SIGNAL("clicked(bool)"), ReceiversLine.close)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL("clicked(bool)"), ReceiversLine.close)
        QtCore.QMetaObject.connectSlotsByName(ReceiversLine)

    def retranslateUi(self, ReceiversLine):
        ReceiversLine.setWindowTitle(QtGui.QApplication.translate("ReceiversLine", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("ReceiversLine", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("ReceiversLine", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        
##########################################################################################################
        
class uiBodyForm(object):
    # Formula Editor
    def setupUi(self, Form):
        self.Form=Form
        Form.setObjectName("Form")
        Form.resize(346, 219)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.formulaLineEdit = QtGui.QLineEdit(Form)
        self.formulaLineEdit.setEnabled(True)
        self.formulaLineEdit.setFrame(False)
        self.formulaLineEdit.setReadOnly(True)
        self.formulaLineEdit.setObjectName("formulaLineEdit")
        self.verticalLayout_2.addWidget(self.formulaLineEdit)
        self.scrollArea = QtGui.QScrollArea(Form)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 130))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 332, 124))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.addExpressionButton = QtGui.QPushButton(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addExpressionButton.sizePolicy().hasHeightForWidth())
        self.addExpressionButton.setSizePolicy(sizePolicy)
        self.font = QtGui.QFont()
        self.font.setPointSize(8)
        self.addExpressionButton.setFont(self.font)
        self.addExpressionButton.setIconSize(QtCore.QSize(14, 14))
        self.addExpressionButton.setObjectName("addExpressionButton")
        self.gridLayout.addWidget(self.addExpressionButton, 0, 0, 1, 1)
        self.spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(self.spacerItem, 0, 1, 1, 1)
        self.addRelationButton = QtGui.QPushButton(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addRelationButton.sizePolicy().hasHeightForWidth())
        self.addRelationButton.setSizePolicy(sizePolicy)
        self.font = QtGui.QFont()
        self.font.setPointSize(8)
        self.addRelationButton.setFont(self.font)
        self.addRelationButton.setObjectName("addRelationButton")
        self.gridLayout.addWidget(self.addRelationButton, 1, 0, 1, 1)
        self.spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(self.spacerItem1, 1, 1, 1, 1)
        self.clearButton = QtGui.QPushButton(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clearButton.sizePolicy().hasHeightForWidth())
        self.clearButton.setSizePolicy(sizePolicy)
        self.font = QtGui.QFont()
        self.font.setPointSize(8)
        self.font.setItalic(False)
        self.font.setUnderline(True)
        self.clearButton.setFont(self.font)
        self.clearButton.setObjectName("clearButton")
        self.gridLayout.addWidget(self.clearButton, 1, 2, 1, 1)
        self.rowEditButton = QtGui.QPushButton(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rowEditButton.sizePolicy().hasHeightForWidth())
        self.rowEditButton.setSizePolicy(sizePolicy)
        self.font = QtGui.QFont()
        self.font.setPointSize(8)
        self.font.setWeight(75)
        self.font.setBold(True)
        self.rowEditButton.setFont(self.font)
        self.rowEditButton.setObjectName("rowEditButton")
        self.gridLayout.addWidget(self.rowEditButton, 0, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.rowEditButton, QtCore.SIGNAL("clicked(bool)"), self.formulaLineEdit.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.addExpressionButton.setText(QtGui.QApplication.translate("Form", "Add Expression", None, QtGui.QApplication.UnicodeUTF8))
        self.addRelationButton.setText(QtGui.QApplication.translate("Form", "Add Relation", None, QtGui.QApplication.UnicodeUTF8))
        self.clearButton.setText(QtGui.QApplication.translate("Form", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.rowEditButton.setText(QtGui.QApplication.translate("Form", "Raw Edit", None, QtGui.QApplication.UnicodeUTF8))

########################################################################################################

class uiRowForm(object):
    # Each of Formula Editor rows
    def setupUi(self, row_widget):
        self.row_widget = row_widget
        row_widget.setObjectName("row_widget")
        row_widget.resize(382, 31)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(row_widget.sizePolicy().hasHeightForWidth())
        row_widget.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(row_widget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName("gridLayout")
        self.valueCombo = QtGui.QComboBox(row_widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.valueCombo.sizePolicy().hasHeightForWidth())
        self.valueCombo.setSizePolicy(sizePolicy)
        self.valueCombo.setObjectName("valueCombo")
        self.valueCombo.addItem(QtCore.QString())
        self.valueCombo.setItemText(0, "")
        self.valueCombo.addItem(QtCore.QString("<"))
        self.valueCombo.addItem(QtCore.QString("<="))
        self.valueCombo.addItem(QtCore.QString("=="))
        self.valueCombo.addItem(QtCore.QString(">"))
        self.valueCombo.addItem(QtCore.QString(">="))
        self.valueCombo.addItem(QtCore.QString("!="))
        self.gridLayout.addWidget(self.valueCombo, 1, 1, 1, 1)

        self.operatorCombo = QtGui.QComboBox(row_widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.operatorCombo.sizePolicy().hasHeightForWidth())
        self.operatorCombo.setSizePolicy(sizePolicy)
        self.operatorCombo.setEditable(True)
        self.operatorCombo.setFrame(True)
        self.operatorCombo.setObjectName("operatorCombo")
        self.gridLayout.addWidget(self.operatorCombo, 1, 2, 1, 1)

        self.variableCombo = QtGui.QComboBox(row_widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.variableCombo.sizePolicy().hasHeightForWidth())
        self.variableCombo.setSizePolicy(sizePolicy)
        self.variableCombo.setEditable(True)
        self.variableCombo.setObjectName("variableCombo")
        self.gridLayout.addWidget(self.variableCombo, 1, 0, 1, 1)

        self.removeButton = QtGui.QPushButton(row_widget)
        self.removeButton.setObjectName("removeButton")
        self.removeButton.setIcon(getThemeIcon("list-remove"))
        self.gridLayout.addWidget(self.removeButton, 1, 3, 1, 1)
        self.retranslateUi(row_widget)

        QtCore.QObject.connect(self.variableCombo, QtCore.SIGNAL("editTextChanged(QString)"), self.row_widget.CreateText)
        QtCore.QObject.connect(self.operatorCombo, QtCore.SIGNAL("editTextChanged(QString)"), self.row_widget.CreateText)
        QtCore.QObject.connect(self.valueCombo, QtCore.SIGNAL("currentIndexChanged(QString)"), self.row_widget.CreateText)
        QtCore.QMetaObject.connectSlotsByName(row_widget)

    def retranslateUi(self, row_widget):
        row_widget.setWindowTitle(QtGui.QApplication.translate("row_widget", "Form", None, QtGui.QApplication.UnicodeUTF8))