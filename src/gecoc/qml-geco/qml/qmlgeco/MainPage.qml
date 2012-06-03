import QtQuick 1.1
import com.nokia.symbian 1.1

import "sha256.js" as Sha256;
import "md5.js" as Md5;
import "aes.js" as SlowAes;
import "gecojs.js" as GECO;

import "query.js" as JS

Page {
    id: mainPage

    Component.onCompleted: {
        JS.base = "http://localhost:8080";
        JS.user = "danigm";
        JS.pwd = "1234";

        JS.load("auth?user="+JS.user+"&password="+JS.pwd,
                function (jsonObject) {
                    JS.cookie = jsonObject.data;
                    JS.load("get_all_passwords?cookie="+JS.urlencode(JS.cookie),
                            function (jsonObject) {
                                var pwdlist = jsonObject.data;
                                pwdlist.sort(function(a, b) {
                                    if (a.name < b.name)
                                        return -1;
                                    if (a.name == b.name)
                                        return 0;
                                    return 1;
                                });

                                for (var i=0; i < pwdlist.length; i++) {
                                    listModel.append(pwdlist[i]);
                                }
                            });
                });
    }

    ListModel { id:listModel }

    ListView {
        id: view
        anchors.fill: parent
        model: listModel
        delegate: Rectangle {
             width: parent.width
             height: 80

             Text {
                 id: pwdName
                anchors.left: parent.left
                text: name
                width: parent.width / 2.0

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        console.log(GECO.decrypt("123", password));
                    }
                }
             }

             Text {
                id: pwdAcc
                anchors.left: pwdName.right
                text: account
                width: parent.width / 2.0

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        console.log(account);
                    }
                }
             }
        }
    }
}
