import QtQuick 1.0

import org.kde.plasma.core 0.1 as PlasmaCore
import org.kde.plasma.components 0.1 as PlasmaComponents

import "qmlgeco/sha256.js" as Sha256;
import "qmlgeco/md5.js" as Md5;
import "qmlgeco/aes.js" as SlowAes;
import "qmlgeco/gecojs.js" as GECO;

import "qmlgeco/query.js" as JS

Item {
    id: main

    PlasmaCore.Theme {
        id: theme
    }

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

                                filterModel();
                            });
                });
    }

    function filterModel() {
        filteredModel.clear();
        for (var i=0; i < listModel.count; i++) {
            var pwd = listModel.get(i);
            var regx = ".*" + searchField.text + ".*";
            var reg = new RegExp(regx, "i");

            if (pwd.name.match(reg)) {
                filteredModel.append(pwd);
            }
        }
    }

    ListModel { id:listModel }
    ListModel { id:filteredModel }

    PlasmaComponents.TextField {
       id: searchField
       anchors.left: parent.left
       anchors.right: parent.right

       onTextChanged: {
           filterModel();
       }
    }

    Item {
        id: buttons
        width: parent.width
        anchors.bottom: parent.bottom

        PlasmaComponents.Button {
            id: refresh
            anchors.left: parent.left
            width: parent.width / 3.0
            iconSource: 'view-refresh'
            text: ''
        }
        PlasmaComponents.Button {
            id: forget
            anchors.left: refresh.right
            width: parent.width / 3.0
            iconSource: 'edit-clear'
            text: ''
        }
        PlasmaComponents.Button {
            id: config
            anchors.left: forget.right
            width: parent.width / 3.0
            iconSource: 'configure'
            text: ''
        }
    }

    ListView {
        id: view
        anchors.top: searchField.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: buttons.top

        model: filteredModel
        clip: true
        delegate: PlasmaComponents.ListItem {
            width: parent.width

             Text {
                 id: pwdName
                anchors.left: parent.left
                text: name
                width: parent.width / 2.0
                elide: Text.ElideRight

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        //console.log(GECO.decrypt("123", password));
                    }
                }
             }

             Text {
                id: pwdAcc
                anchors.left: pwdName.right
                text: account
                width: parent.width / 2.0
                elide: Text.ElideRight

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
