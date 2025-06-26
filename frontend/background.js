chrome.cookies.getAll({domain: "ticktick.com"}, (cookies) => {
    console.log("Ticktick cookies:", cookies);
});
