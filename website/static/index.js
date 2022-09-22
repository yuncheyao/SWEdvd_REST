function deleteCard(cardId) {
    fetch("/delete-card", {
      method: "POST",
      body: JSON.stringify({ cardId: cardId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }