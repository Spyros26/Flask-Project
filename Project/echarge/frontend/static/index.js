function deleteSession(sessionId) {
    fetch("/delete-session", {
      method: "POST",
      body: JSON.stringify({ sessionId: sessionId }),
    }).then((_res) => {
      window.location.href = "/evcharge/api/issue-statement";
    });
  }

  