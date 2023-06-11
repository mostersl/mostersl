import csv
import json
import os
import sys
import threading

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTreeWidgetItem, QMenu, QGraphicsScene, QGraphicsPixmapItem, \
    QGraphicsView, QInputDialog, QLineEdit
from barcode import *
from barcode.writer import ImageWriter
import pandas as pd
from res.untitled import Ui_Form
from src.api import *
from src.write_csv import *

PUBLIC_KEY = """-----BEGIN RSA PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1urQo4aFS7kIuCsHSnArGYftEVoXTBosCQG+sCPDv6owvITvaMy5usPiI5r155iYt/PLqE823nT5OqEgTW6Y1zhLHWrEkf2TR003+moIoF8st5iOhSZvsGwHOciL5tur9ur0xoXhxukK4YjZliHYpZVJrV7PPvmjoUbdIr1IjQf8YTXtwGYh4Ic5tEARejSfxDFDSs5V5kcVRoLXCPFtTResWg2CseO0RoxCM/uBQp4ZTBRbuKDQxUrsX0BfvzL85OaYDSKZeoFNrDkeji6vGhFjRRD4IMdGuLImhC8IvcsCA9GFcgX3zy55UYLterdwgBSHueSTrwq4psp9DLu/AQIDAQAB
-----END RSA PUBLIC KEY-----"""
head = ['快递员名字', '订单号']


class MainWindow(QMainWindow, Ui_Form):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.list_data = []
        self.lp_num = 0
        self.sms_code = 0
        if not os.path.exists('./cache'):
            os.mkdir('./cache')
            os.mkdir('./cache/pic')
            with open('./cache/op.pem', 'w') as f:
                f.write(PUBLIC_KEY)
            create()
        self.pushButton.clicked.connect(self.login)
        self.pushButton_3.clicked.connect(self.sms_login)
        self.pushButton_2.clicked.connect(self.yt_login)
        self.listWidget.doubleClicked.connect(self.DoubleList)
        self.treeWidget.setColumnWidth(4, 130)
        self.treeWidget.setColumnWidth(3, 140)
        self.treeWidget.setColumnWidth(2, 70)
        self.treeWidget.setColumnWidth(5, 70)
        self.tree = None
        s = datetime.now().strftime('%Y-%m-%d').split('-')
        b_date = datetime(int(s[0]), int(s[1]), int(s[2]), 0, 0, 0)
        e_date = datetime(int(s[0]), int(s[1]), int(s[2]), 23, 59, 59)
        self.dateTimeEdit.setDateTime(b_date)
        self.dateTimeEdit_2.setDateTime(e_date)
        self.treeWidget.itemDoubleClicked.connect(self.doubleTree)
        self.treeWidget.itemChanged.connect(self.changeTree)
        self.name = []
        self.readDB()
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested[QtCore.QPoint].connect(self.generateMenu)
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.commandLinkButton.clicked.connect(self.start_up)

    def login(self):
        self.tree = QTreeWidgetItem(self.treeWidget)
        if self.tabWidget.currentIndex() == 0:  # 账号登录
            if self.lineEdit.text() == '' or self.lineEdit_2.text() == '':
                QMessageBox.warning(self, "提示", "请输入账号或密码！")
            else:
                if self.comboBox.currentText() == '中通快递':
                    # self.tree = QTreeWidgetItem(self.treeWidget)
                    account = self.lineEdit.text()
                    password = self.lineEdit_2.text()
                    adss = query(f'select * from INFO where ACCOUNT="{account}"')
                    if len(adss) > 0:
                        devices = list(adss[0])[3]
                    else:
                        devices = str(uuid4())
                        ids = len(query('select ID from INFO')) + 1
                        insert(
                            f'INSERT INTO INFO (ID,ACCOUNT,PASSWORD,DEVICE,FMS,LIST) VALUES ({ids},"{account}","{password}","{devices}","{self.comboBox.currentText()}",0)')
                        self.addCuid()
                    result = ZT_Token(f'{account}:{password}', devices)
                    try:
                        user = ZT_UserInfo(result['access_token'], result['openid'], devices)
                        order_form = ZT_TASK_LIST_V4(result['access_token'], result['openid'], devices,
                                                     self.dateTimeEdit.dateTime().toString('yyyy-MM-dd hh:mm:ss'),
                                                     self.dateTimeEdit_2.dateTime().toString('yyyy-MM-dd hh:mm:ss'))[
                            'result']
                        if len(order_form) > 0:
                            self.tree.setText(3, '请选择')
                            for ih in range(len(order_form)):
                                pol = order_form[ih]
                                childer = QTreeWidgetItem(self.tree)
                                childer.setText(3, pol['billCode'])
                                childer.setCheckState(3, QtCore.Qt.Checked)
                                self.name.append([user['result']['realName'], pol['billCode'] + '\t'])
                        else:
                            self.tree.setText(3, '无')
                        mess = user['message']
                        self.lp_num = self.lp_num + 1
                        self.tree.setText(0, user['result']['realName'])
                        self.tree.setText(1, account)
                        self.tree.setText(2, self.comboBox.currentText())
                        self.tree.setText(4, mess)
                        self.tree.setText(5, f'订单数量：{len(order_form)}')
                        self.tree.setToolTip(4, mess)
                        update(
                            f'UPDATE INFO set MESSAGE = "{mess}",LIST=1,PASSWORD="{password}" where ACCOUNT="{account}"')
                    except KeyError:
                        self.tree.setText(1, account)

                        mes = result['message']
                        self.tree.setText(2, self.comboBox.currentText())
                        self.tree.setText(4, mes)
                        self.tree.setToolTip(4, mes)

                        update(f'UPDATE INFO set MESSAGE = "{mes}",LIST=0 where ACCOUNT="{account}"')
                if self.comboBox.currentText() == '极兔':
                    # self.tree = QTreeWidgetItem(self.treeWidget)
                    account = self.lineEdit.text()
                    password = self.lineEdit_2.text()
                    adss = query(f'select * from INFO where ACCOUNT="{account}"')
                    if len(adss) > 0:
                        devices = list(adss[0])[3]
                    else:
                        devices = "0be9e30b20f7332c4e3377ec7a422b87"
                        ids = len(query('select ID from INFO')) + 1
                        insert(
                            f'INSERT INTO INFO (ID,ACCOUNT,PASSWORD,DEVICE,FMS,LIST) VALUES ({ids},"{account}","{password}","{devices}","{self.comboBox.currentText()}",0)')
                        self.addCuid()
                    result = JT_Login(account, password, devices)
                    try:
                        user = JT_Task_all(account, result['data']['token'],
                                           self.dateTimeEdit.dateTime().toString('yyyy-MM-dd hh:mm:ss'),
                                           self.dateTimeEdit_2.dateTime().toString('yyyy-MM-dd hh:mm:ss'))
                        if len(user['data']) > 0:
                            self.tree.setText(3, '请选择')
                            for ih in range(len(user['data'])):
                                pol = user['data'][ih]
                                childer = QTreeWidgetItem(self.tree)
                                childer.setText(3, pol['waybillNo'])
                                childer.setCheckState(3, QtCore.Qt.Checked)
                                self.name.append([result['data']['name'], pol['waybillNo'] + '\t'])
                        else:
                            self.tree.setText(3, '无')
                        mess = user['msg']
                        self.lp_num = self.lp_num + 1
                        self.tree.setText(0, result['data']['name'])
                        self.tree.setText(1, account)
                        self.tree.setText(2, self.comboBox.currentText())
                        self.tree.setText(4, mess)
                        ss = len(user['data'])
                        self.tree.setText(5, f'订单数量：{ss}')
                        self.tree.setToolTip(4, mess)
                        dec = result['data']['macAddr']
                        update(
                            f'UPDATE INFO set MESSAGE = "{mess}",LIST=1,PASSWORD="{password}",DEVICE="{dec}",FMS="{self.comboBox.currentText()}" where ACCOUNT="{account}"')
                    except KeyError:
                        self.tree.setText(1, account)
                        mes = result['msg']
                        self.tree.setText(2, self.comboBox.currentText())
                        self.tree.setText(4, mes)
                        self.tree.setToolTip(4, mes)
                        update(f'UPDATE INFO set MESSAGE = "{mes}",LIST=0 where ACCOUNT="{account}"')
                if self.comboBox.currentText() == '圆通快递':
                    account = self.lineEdit.text()
                    password = self.lineEdit_2.text()
                    adss = query(f'select * from INFO where ACCOUNT="{account}"')
                    if len(adss) > 0:
                        devices = list(adss[0])[3]
                    else:
                        devices = str(uuid4())
                        ids = len(query('select ID from INFO')) + 1
                        insert(
                            f'INSERT INTO INFO (ID,ACCOUNT,PASSWORD,DEVICE,FMS,LIST) VALUES ({ids},"{account}","{password}","{devices}","{self.comboBox.currentText()}",0)')
                        self.addCuid()
                    result = YT_Login(account, password)
                    try:
                        phone = result['data']['phone']
                        preToken = result['data']['preToken']
                        update(
                            f'UPDATE INFO set LIST=1,PASSWORD="{password}" where ACCOUNT="{account}"')
                        scode = YT_SMS(account, phone, preToken)['data']
                        scount = '总次数：{0} 已发送次数：{1}'.format(scode['totalCount'], scode['sentCount'])
                        value, ok = QInputDialog.getText(self, '输入验证码', phone + f'\n{scount}', QLineEdit.Normal)
                        if ok:
                            res = YT_Login2(account, password, preToken, value)
                            try:
                                order_form = YT_queryList(res['data']['token'])['list']
                                if len(order_form) > 0:
                                    self.tree.setText(3, '请选择')
                                    for ih in range(len(order_form)):
                                        pol = order_form[ih]
                                        childer = QTreeWidgetItem(self.tree)
                                        childer.setText(3, pol['mailNo'])
                                        childer.setCheckState(3, QtCore.Qt.Checked)
                                        self.name.append([res['data']['userName'], pol['mailNo'] + '\t'])
                                else:
                                    self.tree.setText(3, '无')
                                self.tree.setText(0, res['data']['userName'])
                                self.tree.setText(1, account)
                                self.tree.setText(2, self.comboBox.currentText())
                                self.tree.setText(4, res['message'])
                                self.tree.setText(5, f'订单数量：{len(order_form)}')
                                self.tree.setToolTip(4, res['message'])
                            except KeyError:
                                self.tree.setText(1, account)
                                mes = res['message']
                                self.tree.setText(2, self.comboBox.currentText())
                                self.tree.setText(4, mes)
                                self.tree.setToolTip(4, mes)
                    except KeyError:
                        self.tree.setText(1, account)
                        mes = result['message']
                        self.tree.setText(2, self.comboBox.currentText())
                        self.tree.setText(4, mes)
                        self.tree.setToolTip(4, mes)
                        update(f'UPDATE INFO set MESSAGE = "{mes}",LIST=0 where ACCOUNT="{account}"')
                self.tree.treeWidget().scrollToBottom()
        else:
            pass

    def yt_login(self):
        if self.sms_code == 1:
            self.sms_code = 0
            self.tree = QTreeWidgetItem(self.treeWidget)
            adss = query(f'select * from INFO where ACCOUNT="{self.lineEdit_3.text()}"')
            if len(adss) > 0:
                devices = list(adss[0])[3]
            else:
                devices = str(uuid4())
                ids = len(query('select ID from INFO')) + 1
                insert(
                    f'INSERT INTO INFO (ID,ACCOUNT,DEVICE,FMS,LIST) VALUES ({ids},"{self.lineEdit_3.text()}","{devices}","{self.comboBox.currentText()}",0)')
                self.addCuid()
            result = ST_Login(self.lineEdit_3.text(), self.lineEdit_4.text())
            self.pushButton_3.setText('获取')
            self.pushButton_3.setEnabled(True)
            if len(result['data']) > 10:
                update(
                    f'UPDATE INFO set LIST=1 where ACCOUNT="{self.lineEdit_3.text()}"')
                jishu = 0
                tokens = result['data']['token']
                user = ST_getUser(tokens)
                st_list = ST_queryList(tokens)['data']
                if len(st_list['groups']) > 0:
                    for i in range(len(st_list['groups'])):
                        if st_list['groups'][i]['text'] != '拦截件':
                            records = st_list['groups'][i]['records']
                            for j in range(len(records)):
                                ddh = records[j]['waybillNo']
                                childer = QTreeWidgetItem(self.tree)
                                childer.setText(3, ddh)
                                childer.setCheckState(3, QtCore.Qt.Checked)
                                jishu = jishu + 1
                                self.name.append([user['data']['userList'][0]['nickName'], ddh + '\t'])
                else:
                    self.tree.setText(3, '无')
                self.tree.setText(0, user['data']['userList'][0]['nickName'])
                self.tree.setText(1, self.lineEdit_3.text())
                self.tree.setText(2, self.comboBox.currentText())
                self.tree.setText(4, '登陆成功')
                self.tree.setText(5, f'订单数量：{jishu}')
                self.tree.setToolTip(4, '登陆成功')
            else:
                self.tree.setText(1, self.lineEdit_3.text())
                mes = result['resMessage']
                self.tree.setText(2, self.comboBox.currentText())
                self.tree.setText(4, mes)
                self.tree.setToolTip(4, mes)
        else:
            QMessageBox.information(self, "提示", "验证码未输入或重复")

    def yzm(self, data):
        while True:
            data = data - 1
            self.pushButton_3.setText(str(data))
            if data == 0:
                self.pushButton_3.setText('获取')
                self.pushButton_3.setEnabled(True)
                break
            time.sleep(1)

    def sms_login(self):
        if self.tabWidget.currentIndex() == 1:  # 账号登录
            if self.lineEdit_3.text() == '':
                QMessageBox.warning(self, "提示", "请输入手机号！")
            else:
                if self.comboBox_2.currentText() == '申通快递':
                    self.sms_code = 1
                    ST_sendAuthCode(self.lineEdit_3.text())
                    self.pushButton_3.setEnabled(False)
                    t1 = threading.Thread(target=self.yzm, args=(60,))
                    t1.start()

    def readDB(self):
        try:
            self.updateList()
        except:
            pass

    def start_up(self):
        if len(self.name) > 0:
            self.commandLinkButton.setEnabled(False)
            tb = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            ts = time.strftime('%H.%M.%S', time.localtime(time.time()))
            if not os.path.exists(f'./{tb}'):
                os.mkdir(f'./{tb}')
            pd.DataFrame(self.name).to_csv(f'./{tb}/订单号 {ts}.csv', header=head)
            QMessageBox.information(self, "提示", "提取成功")
            self.commandLinkButton.setEnabled(True)

    def updateList(self):
        listTexts = []
        f = query(f'select * from INFO where LIST=1')
        if len(f) > 0:
            for i in f:
                listTexts.append(list(i)[1])
            self.listWidget.clear()
            self.listWidget.addItems(listTexts)

    def addCuid(self):
        self.listWidget.addItem(self.lineEdit.text().replace(" ", ""))

    def generateMenu(self):
        menu = QMenu(self)
        clear = menu.addAction("删除")
        acc = self.listWidget.item(self.listWidget.currentRow()).text()
        update(f'UPDATE INFO set LIST = 0 where ACCOUNT="{acc}"')
        clear.triggered.connect(lambda: self.listWidget.takeItem(self.listWidget.currentRow()))
        menu.exec_(QCursor.pos())

    def doubleTree(self, item, column):
        if len(item.text(column)) > 10:
            number = item.text(column)
            my_code = Code128(number, writer=ImageWriter())
            my_code.save(f'./cache/pic/{number}')
            self.openPic(f'./cache/pic/{number}.png')

    def changeTree(self, item, column):
        # if item.checkState(column) == QtCore.Qt.Checked:
        #     self.name.append([,f'{item.text(column)}\t'])
        if item.checkState(column) == QtCore.Qt.Unchecked:
            try:
                for x in range(len(self.name)):
                    if self.name[x][1] == f'{item.text(column)}\t':
                        del self.name[x]
                        print(self.name)
                        break
            except ValueError:
                pass

    def DoubleList(self):
        data = query(f'select * from INFO where ACCOUNT="{self.listWidget.item(self.listWidget.currentRow()).text()}"')
        account = list(data[0])[2]
        lx = list(data[0])[4]
        if lx == '申通快递':
            self.tabWidget.setCurrentIndex(1)
        if self.tabWidget.currentIndex() == 1:
            self.lineEdit_3.setText(self.listWidget.item(self.listWidget.currentRow()).text())
            self.comboBox_2.setCurrentText(lx)
        else:
            self.lineEdit.setText(self.listWidget.item(self.listWidget.currentRow()).text())
            self.lineEdit_2.setText(account)
            self.comboBox.setCurrentText(lx)

    def openPic(self, fileName):
        self.graphicsView.scene_img = QGraphicsScene()
        self.imgShow = QPixmap()
        self.imgShow.load(fileName)
        self.imgShowItem = QGraphicsPixmapItem()
        self.imgShowItem.setPixmap(QPixmap(self.imgShow))
        self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.scene_img.addItem(self.imgShowItem)
        self.graphicsView.setScene(self.graphicsView.scene_img)
        scene = self.graphicsView.scene()
        r = scene.sceneRect()
        self.graphicsView.fitInView(r, 0)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    ui = MainWindow()
    ui.show()
    # ui.initData(app.exec_())
    sys.exit(app.exec_())
