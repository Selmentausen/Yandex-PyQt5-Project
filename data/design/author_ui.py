# -*- coding: utf-8 -*-

# Form implementation generated from reading design file 'data/author.design'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.imageLabel = QtWidgets.QLabel(Form)
        self.imageLabel.setText("")
        self.imageLabel.setObjectName("imageLabel")
        self.horizontalLayout.addWidget(self.imageLabel)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.nameLabel = QtWidgets.QLabel(Form)
        self.nameLabel.setText("")
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameLabel)
        self.birthdayLabel = QtWidgets.QLabel(Form)
        self.birthdayLabel.setText("")
        self.birthdayLabel.setObjectName("birthdayLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.birthdayLabel)
        self.horizontalLayout.addLayout(self.formLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Author"))
        self.label_2.setText(_translate("Form", "Name:"))
        self.label_3.setText(_translate("Form", "Birthday:"))
