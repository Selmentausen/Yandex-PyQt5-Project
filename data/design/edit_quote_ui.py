# -*- coding: utf-8 -*-

# Form implementation generated from reading design file 'data/edit_quote.design'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 236)
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.quoteLabel = QtWidgets.QLabel(Form)
        self.quoteLabel.setObjectName("quoteLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.quoteLabel)
        self.quoteTextEdit = QtWidgets.QTextEdit(Form)
        self.quoteTextEdit.setObjectName("quoteTextEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.quoteTextEdit)
        self.submitPushButton = QtWidgets.QPushButton(Form)
        self.submitPushButton.setObjectName("submitPushButton")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.submitPushButton)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Edit quote"))
        self.quoteLabel.setText(_translate("Form", "Quote"))
        self.submitPushButton.setText(_translate("Form", "OK"))
