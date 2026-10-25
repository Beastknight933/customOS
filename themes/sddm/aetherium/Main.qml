import QtQuick
import QtQuick.Window
import Qt5Compat.GraphicalEffects
import Qt.labs.folderlistmodel
import SddmComponents 2.0

Rectangle {
    id: root

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.ArrowCursor
        z: -1
    }

    readonly property real s: Screen.height / 768
    width: Screen.width
    height: Screen.height
    color: root.bgColor

    property bool isQuickshell: typeof sddm === "undefined" || sddm.hostName === undefined

    // Configuration & Visual Tokens
    readonly property string themeMode: config.themeMode || "dark"
    readonly property bool enableWindup: config.enableWindup !== "false" && config.enableWindup !== false
    readonly property bool isLight: themeMode === "light"

    // Aetherium Design Palette
    readonly property color bgColor: isLight ? "#f8fafc" : "#090c10"
    readonly property color mainText: isLight ? "#0f172a" : "#e8edf5"
    readonly property color dimText: isLight ? "#64748b" : "#8b9bb4"
    readonly property color subColor: isLight ? "#475569" : "#5c6b84"
    readonly property color pillColor: isLight ? "#e2e8f0" : "#101522"
    readonly property color pillBorder: isLight ? (root.isWindup ? "#94a3b8" : "#cbd5e1") : (root.isWindup ? "#60a5fa" : "#1e293b")
    readonly property color pillInnerLine: isLight ? "#0f172a" : "#60a5fa"
    readonly property color sparkColor: isLight ? "#2563eb" : "#60a5fa"
    readonly property color blastColor: isLight ? "#ffffff" : "#60a5fa"
    readonly property color userItemInactive: isLight ? "#94a3b8" : "#475569"
    readonly property color inputWaitColor: isLight ? "#94a3b8" : "#334155"
    readonly property color accentColor: "#60a5fa"

    // State Management
    property int sessionIndex: (typeof sessionModel !== "undefined" && sessionModel.lastIndex >= 0) ? sessionModel.lastIndex : 0
    property int userIndex: (typeof userModel !== "undefined" && userModel.lastIndex >= 0) ? userModel.lastIndex : 0
    property bool userMenuOpen: false
    property bool isWindup: false
    property real uiOpacity: 0
    readonly property real marginR: 80 * s

    // Time Tracking with Millisecond Precision
    property int curH: new Date().getHours()
    property int curM: new Date().getMinutes()
    property int curS: new Date().getSeconds()
    property int curMS: new Date().getMilliseconds()
    readonly property real localTimeMS: (curH * 3600000) + (curM * 60000) + (curS * 1000) + curMS

    Timer {
        interval: 16
        running: true
        repeat: true
        onTriggered: {
            var d = new Date()
            root.curH = d.getHours()
            root.curM = d.getMinutes()
            root.curS = d.getSeconds()
            root.curMS = d.getMilliseconds()
        }
    }

    // Dynamic Windup & Boom Animations
    property real windupOffset: 0
    property real windupProgress: windupOffset / 150000
    property real boomScale: 1.0
    property real boomOpacity: 0.0
    property real jitterX: 0
    property real jitterY: 0
    property real sparkIntensity: 0.0

    Timer {
        interval: 16
        running: root.isWindup
        repeat: true
        onTriggered: {
            var intensity = root.windupProgress * 32 * s
            root.jitterX = (Math.random() - 0.5) * intensity
            root.jitterY = (Math.random() - 0.5) * intensity
            root.sparkIntensity = root.windupProgress > 0.2 ? (root.windupProgress - 0.2) * 2.2 : 0
        }
    }

    NumberAnimation {
        id: windupAnim
        target: root
        property: "windupOffset"
        from: 0
        to: 150000
        duration: 1600
        easing.type: Easing.InQuint
    }

    ParallelAnimation {
        id: boomSequence
        onFinished: root.doLogin()
        NumberAnimation { target: root; property: "boomScale"; to: 35.0; duration: 150; easing.type: Easing.InQuad }
        NumberAnimation { target: root; property: "boomOpacity"; to: 1.0; duration: 120; easing.type: Easing.InQuad }
    }

    readonly property real smoothSecAngle: -((localTimeMS % 60000) / 60000.0) * 360.0 - windupOffset * 10.0
    readonly property real smoothMinAngle: -((localTimeMS % 3600000) / 3600000.0) * 360.0 - windupOffset * 5.0

    // Typography Loader
    FolderListModel { id: fontFolder; folder: Qt.resolvedUrl("font"); nameFilters: ["*.ttf", "*.otf"] }
    FontLoader { id: mainFont; source: fontFolder.count > 0 ? "font/" + fontFolder.get(0, "fileName") : "" }
    TextConstants { id: textConstants }

    // Helpers
    ListView {
        id: userHelper
        width: 1
        height: 1
        opacity: 0
        currentIndex: root.userIndex
        model: typeof userModel !== "undefined" ? userModel : null
        delegate: Item {
            property string uName: model.realName || model.name || ""
            property string uLogin: model.name || ""
        }
    }

    ListView {
        id: sessionHelper
        width: 1
        height: 1
        opacity: 0
        currentIndex: root.sessionIndex
        model: typeof sessionModel !== "undefined" ? sessionModel : null
        delegate: Item {
            property string sName: model.name || ""
        }
    }

    Timer {
        interval: 300
        running: true
        onTriggered: passInput.forceActiveFocus()
    }

    Component.onCompleted: {
        fadeIn.start()
        if (typeof keyboard !== "undefined") keyboard.numLock = true
    }

    NumberAnimation {
        id: fadeIn
        target: root
        property: "uiOpacity"
        to: 1
        duration: 350
        easing.type: Easing.OutCubic
    }

    // Static/Dynamic Background
    Image {
        id: bgImage
        anchors.fill: parent
        source: config.background || "assets/background.png"
        fillMode: Image.PreserveAspectCrop
        opacity: 0.45
        visible: status === Image.Ready
    }

    // Main Visual Layer
    Item {
        id: blastContainer
        anchors.fill: parent
        opacity: root.uiOpacity
        x: root.jitterX
        y: root.jitterY
        transform: Scale {
            origin.x: 400 * s
            origin.y: blastContainer.height * 0.5
            xScale: root.boomScale
            yScale: root.boomScale
        }

        Item {
            id: clockContainer
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            width: 800 * s
            height: parent.height
            readonly property real cx: 40 * s
            readonly property real cy: height * 0.5
            readonly property real minR: 320 * s
            readonly property real secR: 480 * s

            Rectangle {
                id: indicatorPill
                z: 1
                x: clockContainer.cx + 230 * s
                anchors.verticalCenter: parent.verticalCenter
                width: 330 * s
                height: 90 * s
                radius: 45 * s
                color: root.pillColor
                border.color: root.pillBorder
                border.width: 1 * s

                Rectangle {
                    x: 170 * s
                    anchors.verticalCenter: parent.verticalCenter
                    width: 1 * s
                    height: 35 * s
                    color: root.pillInnerLine
                }
            }

            // Orbital Minute Ring
            Repeater {
                model: 60
                delegate: Item {
                    z: 10
                    property real base: index * 6
                    property real relAngle: {
                        var a = (base + root.smoothMinAngle) % 360
                        if (a > 180) a -= 360
                        if (a < -180) a += 360
                        return a
                    }
                    property real spotlight: Math.max(0, 1.0 - Math.abs(relAngle) / 4.0)
                    property bool isMajor: index % 5 == 0
                    property real disp: (base + root.smoothMinAngle) * Math.PI / 180
                    property real tx: clockContainer.cx + clockContainer.minR * Math.cos(disp)
                    property real ty: clockContainer.cy + clockContainer.minR * Math.sin(disp)
                    visible: tx > -600 * s && tx < 1800 * s

                    Rectangle {
                        x: parent.tx - width / 2
                        y: parent.ty - height / 2
                        width: isMajor ? 2 * s : 1 * s
                        height: isMajor ? 18 * s : 10 * s
                        color: spotlight > 0 ? root.accentColor : Qt.rgba(1, 1, 1, isMajor ? 0.35 : 0.15)
                        rotation: disp * 180 / Math.PI + 90
                        antialiasing: true
                        transformOrigin: Item.Center
                    }

                    Text {
                        visible: isMajor
                        property real nRad: clockContainer.minR - 35 * s
                        x: clockContainer.cx + nRad * Math.cos(disp) - width / 2
                        y: clockContainer.cy + nRad * Math.sin(disp) - height / 2
                        text: String(index).padStart(2, '0')
                        font.family: mainFont.name
                        font.pixelSize: 22 * s
                        font.weight: spotlight > 0.5 ? Font.Bold : Font.Normal
                        color: spotlight > 0 ? root.accentColor : Qt.rgba(1, 1, 1, 0.4)
                        rotation: disp * 180 / Math.PI
                        transformOrigin: Item.Center
                        antialiasing: true
                    }
                }
            }

            // Orbital Second Ring
            Repeater {
                model: 60
                delegate: Item {
                    z: 10
                    property real base: index * 6
                    property real relAngle: {
                        var a = (base + root.smoothSecAngle) % 360
                        if (a > 180) a -= 360
                        if (a < -180) a += 360
                        return a
                    }
                    property real spotlight: Math.max(0, 1.0 - Math.abs(relAngle) / 4.0)
                    property bool isMajor: index % 5 == 0
                    property real disp: (base + root.smoothSecAngle) * Math.PI / 180
                    property real tx: clockContainer.cx + clockContainer.secR * Math.cos(disp)
                    property real ty: clockContainer.cy + clockContainer.secR * Math.sin(disp)
                    visible: tx > -600 * s && tx < 1800 * s

                    Rectangle {
                        x: parent.tx - width / 2
                        y: parent.ty - height / 2
                        width: isMajor ? 1.5 * s : 1 * s
                        height: isMajor ? 13 * s : 8 * s
                        color: spotlight > 0 ? root.accentColor : Qt.rgba(1, 1, 1, isMajor ? 0.25 : 0.1)
                        rotation: disp * 180 / Math.PI + 90
                        antialiasing: true
                        transformOrigin: Item.Center
                    }

                    Text {
                        visible: isMajor
                        property real nRad: clockContainer.secR - 30 * s
                        x: clockContainer.cx + nRad * Math.cos(disp) - width / 2
                        y: clockContainer.cy + nRad * Math.sin(disp) - height / 2
                        text: String(index).padStart(2, '0')
                        font.family: mainFont.name
                        font.pixelSize: 16 * s
                        font.weight: spotlight > 0.5 ? Font.Bold : Font.Normal
                        color: spotlight > 0 ? root.accentColor : Qt.rgba(1, 1, 1, 0.3)
                        rotation: disp * 180 / Math.PI
                        transformOrigin: Item.Center
                        antialiasing: true
                    }
                }
            }

            // Hours & Date Display
            Text {
                anchors.right: indicatorPill.left
                anchors.rightMargin: 40 * s
                anchors.verticalCenter: parent.verticalCenter
                text: String(root.curH).padStart(2, '0')
                font.family: mainFont.name
                font.pixelSize: 110 * s
                font.weight: Font.Black
                color: root.mainText
            }

            Column {
                anchors.left: indicatorPill.right
                anchors.leftMargin: 110 * s
                anchors.verticalCenter: parent.verticalCenter
                spacing: 5 * s

                Text {
                    text: Qt.formatDate(new Date(), "dd MMM yyyy").toUpperCase()
                    font.family: mainFont.name
                    font.pixelSize: 13 * s
                    font.letterSpacing: 4 * s
                    color: root.subColor
                }

                Text {
                    text: Qt.formatDate(new Date(), "dddd").toUpperCase()
                    font.family: mainFont.name
                    font.pixelSize: 18 * s
                    font.letterSpacing: 8 * s
                    font.weight: Font.Bold
                    color: root.mainText
                }
            }
        }
    }

    // Flash Transition
    Rectangle {
        anchors.fill: parent
        color: root.blastColor
        opacity: root.boomOpacity
        z: 9999
    }

    // Interactive HUD
    Item {
        id: hudContainer
        anchors.fill: parent
        opacity: root.uiOpacity * (root.boomOpacity > 0 ? 0 : 1)

        // Title Branding
        Text {
            anchors.left: parent.left
            anchors.leftMargin: 60 * s
            anchors.top: parent.top
            anchors.topMargin: 50 * s
            text: config.title || "AETHERIUM OS"
            font.family: mainFont.name
            font.pixelSize: 14 * s
            font.letterSpacing: 6 * s
            font.weight: Font.Bold
            color: root.subColor
        }

        // Top Right Actions (Session / Reboot / Power)
        Row {
            anchors.right: parent.right
            anchors.rightMargin: root.marginR
            anchors.top: parent.top
            anchors.topMargin: 50 * s
            spacing: 25 * s

            AeAction {
                visible: !root.isQuickshell
                label: (sessionHelper.currentItem ? sessionHelper.currentItem.sName : "Session")
                onClicked: {
                    if (typeof sessionModel !== "undefined" && sessionModel.rowCount() > 0)
                        root.sessionIndex = (root.sessionIndex + 1) % sessionModel.rowCount()
                }
            }

            Rectangle {
                visible: !root.isQuickshell
                width: 1 * s
                height: 10 * s
                color: root.pillBorder
                anchors.verticalCenter: parent.verticalCenter
            }

            AeAction {
                label: "Reboot"
                onClicked: {
                    if (typeof sddm !== "undefined") sddm.reboot()
                }
            }

            Rectangle {
                width: 1 * s
                height: 10 * s
                color: root.pillBorder
                anchors.verticalCenter: parent.verticalCenter
            }

            AeAction {
                label: "Shutdown"
                onClicked: {
                    if (typeof sddm !== "undefined") sddm.powerOff()
                }
            }
        }

        // User Selection Popup
        Item {
            id: uMenuContainer
            z: 6000
            anchors.bottom: loginPanel.top
            anchors.bottomMargin: 15 * s
            anchors.right: loginPanel.right
            width: 280 * s
            height: root.userMenuOpen ? ((typeof userModel !== "undefined" ? userModel.rowCount() : 0) * 30 * s) + 20 * s : 0
            clip: true

            Behavior on height {
                NumberAnimation { duration: 400; easing.type: Easing.OutExpo }
            }

            Column {
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                spacing: 6 * s

                Repeater {
                    model: typeof userModel !== "undefined" ? userModel : null
                    delegate: Item {
                        width: 260 * s
                        height: 26 * s
                        property bool itemHover: uItemMa.containsMouse

                        Text {
                            id: uItemTxt
                            text: (model.realName || model.name || "").toUpperCase()
                            font.family: mainFont.name
                            font.pixelSize: 13 * s
                            font.letterSpacing: 2 * s
                            color: (root.userIndex === index || itemHover) ? root.mainText : root.userItemInactive
                            anchors.right: parent.right
                            anchors.rightMargin: itemHover ? 30 * s : 10 * s
                            anchors.verticalCenter: parent.verticalCenter
                            Behavior on anchors.rightMargin { NumberAnimation { duration: 200 } }
                        }

                        Text {
                            text: "✦"
                            anchors.left: uItemTxt.right
                            anchors.leftMargin: 8 * s
                            anchors.verticalCenter: parent.verticalCenter
                            color: root.accentColor
                            opacity: itemHover ? 1.0 : 0
                            font.pixelSize: 10 * s
                            Behavior on opacity { NumberAnimation { duration: 200 } }
                        }

                        MouseArea {
                            id: uItemMa
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                root.userIndex = index
                                root.userMenuOpen = false
                            }
                        }
                    }
                }
            }
        }

        // Login Panel & Password Input
        Column {
            id: loginPanel
            anchors.right: parent.right
            anchors.rightMargin: root.marginR
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 80 * s
            width: 350 * s
            spacing: 8 * s

            Item {
                width: parent.width
                height: 32 * s
                z: 5000

                Text {
                    id: userNameDisp
                    anchors.right: parent.right
                    anchors.rightMargin: (uMa.containsMouse || root.userMenuOpen) ? 25 * s : 0
                    text: ((userHelper.currentItem && userHelper.currentItem.uName) ? userHelper.currentItem.uName : ((typeof userModel !== "undefined" && userModel.lastUser) ? capitalizeFirst(userModel.lastUser) : "USER")).toUpperCase()
                    font.family: mainFont.name
                    font.pixelSize: 18 * s
                    font.weight: Font.Bold
                    font.letterSpacing: 8 * s
                    color: (uMa.containsMouse || root.userMenuOpen) ? root.mainText : root.dimText
                    Behavior on color { ColorAnimation { duration: 200 } }
                    Behavior on anchors.rightMargin { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }
                }

                Text {
                    text: "✦"
                    anchors.left: userNameDisp.right
                    anchors.leftMargin: 8 * s
                    anchors.verticalCenter: userNameDisp.verticalCenter
                    color: root.accentColor
                    opacity: (uMa.containsMouse || root.userMenuOpen) ? 1.0 : 0
                    font.pixelSize: 12 * s
                    Behavior on opacity { NumberAnimation { duration: 200 } }
                }

                MouseArea {
                    id: uMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: { root.userMenuOpen = !root.userMenuOpen }
                }
            }

            Item {
                width: parent.width
                height: 30 * s

                TextInput {
                    id: passInput
                    anchors.fill: parent
                    echoMode: TextInput.Password
                    passwordCharacter: "✦"
                    color: root.accentColor
                    font.family: mainFont.name
                    font.pixelSize: 14 * s
                    font.letterSpacing: 10 * s
                    horizontalAlignment: TextInput.AlignRight
                    verticalAlignment: TextInput.AlignVCenter
                    focus: true
                    property bool wasClicked: false
                    cursorVisible: false
                    cursorDelegate: Item { width: 0; height: 0 }

                    Keys.onReturnPressed: startLoginSequence()

                    Text {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        text: "ENTER CREDENTIALS"
                        font.family: mainFont.name
                        font.pixelSize: 10 * s
                        font.letterSpacing: 4 * s
                        color: root.inputWaitColor
                        opacity: passInput.text.length === 0 ? 0.5 : 0
                        Behavior on opacity { NumberAnimation { duration: 400; easing.type: Easing.InOutSine } }
                    }

                    Rectangle {
                        id: needleCursor
                        width: 1.5 * s
                        height: 12 * s
                        color: root.accentColor
                        anchors.verticalCenter: parent.verticalCenter
                        x: passInput.cursorRectangle.x
                        visible: passInput.focus && (passInput.text.length > 0 || passInput.wasClicked)

                        SequentialAnimation {
                            loops: Animation.Infinite
                            running: needleCursor.visible
                            NumberAnimation { target: needleCursor; property: "opacity"; from: 1; to: 0.1; duration: 450 }
                            NumberAnimation { target: needleCursor; property: "opacity"; from: 0.1; to: 1; duration: 450 }
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.ArrowCursor
                    onClicked: {
                        passInput.forceActiveFocus()
                        passInput.wasClicked = true
                    }
                }
            }

            Item {
                width: parent.width
                height: 40 * s

                Text {
                    id: loginBtn
                    anchors.right: parent.right
                    anchors.rightMargin: btnMa.containsMouse ? 25 * s : 0
                    text: "AUTHENTICATE"
                    font.family: mainFont.name
                    font.pixelSize: 11 * s
                    font.letterSpacing: 4 * s
                    font.weight: Font.Bold
                    color: passInput.text.length > 0 ? (btnMa.containsMouse ? root.mainText : root.dimText) : "transparent"
                    opacity: passInput.text.length > 0 ? 1.0 : 0
                    Behavior on anchors.rightMargin { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }
                }

                Text {
                    text: "✦"
                    anchors.left: loginBtn.right
                    anchors.leftMargin: 8 * s
                    anchors.verticalCenter: loginBtn.verticalCenter
                    color: root.accentColor
                    opacity: (btnMa.containsMouse && passInput.text.length > 0) ? 1.0 : 0
                    font.pixelSize: 10 * s
                    Behavior on opacity { NumberAnimation { duration: 200 } }
                }

                MouseArea {
                    id: btnMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: { startLoginSequence() }
                }
            }

            Text {
                id: errText
                width: parent.width
                height: 15 * s
                verticalAlignment: Text.AlignBottom
                horizontalAlignment: Text.AlignRight
                text: ""
                color: "#f87171"
                font.family: mainFont.name
                font.pixelSize: 10 * s
                font.letterSpacing: 2 * s
            }
        }
    }

    Timer {
        id: boomTriggerTimer
        interval: 1450
        onTriggered: { boomSequence.start() }
    }

    function startLoginSequence() {
        if (passInput.text.length === 0 || isWindup) return
        if (root.enableWindup) {
            isWindup = true
            windupAnim.start()
            boomTriggerTimer.start()
        } else {
            doLogin()
        }
    }

    function doLogin() {
        var uname = (userHelper.currentItem && userHelper.currentItem.uLogin) ? userHelper.currentItem.uLogin : (typeof userModel !== "undefined" ? userModel.lastUser : "user")
        if (typeof sddm !== "undefined") {
            sddm.login(uname, passInput.text, root.sessionIndex)
        }
    }

    function capitalizeFirst(str) {
        if (!str) return ""
        return str.charAt(0).toUpperCase() + str.slice(1)
    }

    Connections {
        target: typeof sddm !== "undefined" ? sddm : null
        function onLoginSucceeded() { }
        function onLoginFailed() {
            isWindup = false
            windupAnim.stop()
            boomTriggerTimer.stop()
            boomSequence.stop()
            root.windupOffset = 0
            root.boomScale = 1.0
            root.boomOpacity = 0.0
            root.sparkIntensity = 0
            errText.text = "AUTHENTICATION FAILED"
            passInput.text = ""
            passInput.forceActiveFocus()
            shake.start()
        }
    }

    SequentialAnimation {
        id: shake
        NumberAnimation { target: loginPanel; property: "anchors.rightMargin"; from: root.marginR; to: root.marginR + 10 * s; duration: 50; easing.type: Easing.InOutSine }
        NumberAnimation { target: loginPanel; property: "anchors.rightMargin"; to: root.marginR - 10 * s; duration: 50; easing.type: Easing.InOutSine }
        NumberAnimation { target: loginPanel; property: "anchors.rightMargin"; to: root.marginR; duration: 50; easing.type: Easing.InOutSine }
    }

    component AeAction: Item {
        id: actItem
        width: actTxt.width + 20 * s
        height: 15 * s
        property string label: ""
        signal clicked()

        Text {
            id: actTxt
            anchors.right: parent.right
            anchors.rightMargin: actM.containsMouse ? 15 * s : 0
            text: label.toUpperCase()
            color: actM.containsMouse ? root.mainText : root.dimText
            font.family: mainFont.name
            font.pixelSize: 10 * s
            font.letterSpacing: 3 * s
            Behavior on color { ColorAnimation { duration: 200 } }
            Behavior on anchors.rightMargin { NumberAnimation { duration: 200 } }
        }

        Text {
            text: "✦"
            anchors.left: actTxt.right
            anchors.leftMargin: 4 * s
            anchors.verticalCenter: actTxt.verticalCenter
            color: root.accentColor
            opacity: actM.containsMouse ? 1.0 : 0
            font.pixelSize: 8 * s
            Behavior on opacity { NumberAnimation { duration: 200 } }
        }

        MouseArea {
            id: actM
            anchors.fill: parent
            hoverEnabled: true
            onClicked: { actItem.clicked() }
            cursorShape: Qt.PointingHandCursor
        }
    }
}
