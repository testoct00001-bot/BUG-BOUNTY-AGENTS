!function(){var t=window.__CFG.api;function n(e){return fetch(t+"/auth/refresh",{method:"POST",body:JSON.stringify({rt:localStorage.getItem("rt")})})}window.App={refresh:n}}();
