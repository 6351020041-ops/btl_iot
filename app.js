// ================= LOAD LOGS =================

async function load() {

    let res = await fetch("/logs");
    let data = await res.json();

    let html = "";

    data.forEach(i => {

        html += `
        <tr>
            <td>${i.uid}</td>
            <td>${i.mssv}</td>
            <td>${i.name}</td>
            <td>${i.class}</td>
            <td>${i.date}</td>
            <td>${i.check_in || "-"}</td>
            <td>${i.check_out || "-"}</td>

            <td class="text-center">
                <button
                    class="btn btn-sm btn-danger"
                    onclick="deleteLog('${i.uid}','${i.date}')">
                    Xóa
                </button>
            </td>
        </tr>
        `;
    });

    document.getElementById("body").innerHTML = html;
}


// ================= ADD STUDENT =================

async function addStudent() {

    let uid = document.getElementById("uid").value.trim();
    let mssv = document.getElementById("mssv").value.trim();
    let name = document.getElementById("name").value.trim();
    let className = document.getElementById("class").value.trim();

    if (!uid || !mssv || !name || !className) {

        document.getElementById("msg2").innerHTML =
            "❌ Vui lòng nhập đầy đủ thông tin";

        return;
    }

    let res = await fetch("/add-student", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            uid: uid,
            mssv: mssv,
            name: name,
            class: className
        })
    });

    let data = await res.json();

    if (data.status === "ok") {

        document.getElementById("msg2").innerHTML =
            "✔ Thêm sinh viên thành công";

        document.getElementById("uid").value = "";
        document.getElementById("mssv").value = "";
        document.getElementById("name").value = "";
        document.getElementById("class").value = "";
    }
}


// ================= DELETE STUDENT =================

async function deleteStudent() {

    let uid = document.getElementById("uid").value.trim();

    if (!uid) {

        alert("Nhập UID cần xóa");
        return;
    }

    if (!confirm("Bạn có chắc muốn xóa sinh viên này?"))
        return;

    let res = await fetch("/delete-student", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            uid: uid
        })
    });

    let data = await res.json();

    document.getElementById("msg2").innerHTML =
        "✔ " + data.msg;

    load();
}


// ================= DELETE LOG =================

async function deleteLog(uid, date) {

    if (!confirm("Xóa bản ghi điểm danh này?"))
        return;

    let res = await fetch("/delete-log", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            uid: uid,
            date: date
        })
    });

    let data = await res.json();

    alert(data.msg);

    load();
}


// ================= RFID SCAN =================

async function scan(uid) {

    let res = await fetch("/scan", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            uid: uid
        })
    });

    let data = await res.json();

    if (data.status === "error") {

        document.getElementById("msg").innerHTML =
            "❌ " + data.msg;
    }
    else {

        document.getElementById("msg").innerHTML =
            "✔ " + data.msg +
            " - " +
            data.name;
    }

    load();
}


// ================= AUTO REFRESH =================

load();

setInterval(() => {
    load();
}, 2000);


// ================= TEST RFID =================

document.addEventListener("keydown", (e) => {

    if (e.key === "1") {
        scan("UID001");
    }

    if (e.key === "2") {
        scan("UID002");
    }

});