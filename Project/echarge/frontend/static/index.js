function deleteSession(sessionId) {
    var datefrom = document.getElementById('dates').innerHTML.substr(5, 10)
    var dateto = document.getElementById('dates').innerHTML.substr(19)
    fetch("/evcharge/api/delete-session", {
      method: "POST",
      body: JSON.stringify({ sessionId: sessionId }),
    }).then((_res) => {
      window.location.href = "/evcharge/api/issue-statement/" + datefrom + "/" + dateto;
    });
  }

  