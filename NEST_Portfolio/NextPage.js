function nextPage(callback) {
    const filter_bar = document.querySelector('.filterbar');
    const pagination = filter_bar.querySelector('.pagination');

    let pages_options = pagination.querySelectorAll('.icon-bas-005');

    new Promise((resolve, _) => {
        if (pages_options === null) {
            console.log("Next page option is null")
            const observer = new MutationObserver((mutations, observer) => {
                console.log("Inside the observer for the next page option.")
                for (let mutation of mutations) {
                    if (mutation.type === 'childList') {
                        for (let node of mutation.addedNodes) {
                            if (node.getAttribute('class') === 'icon-bas-005') {
                                pages_options = pagination.querySelectorAll('.icon-bas-005');
                                observer.disconnect();
                            }
                        }
                    }
                }
            });
            observer.observe(pagination, {childList: true});
            resolve();
        } else {
            resolve();
        }
    }).then(() => {
        if (pages_options.length === 2) {
            const next_page = pages_options[1];
            new Promise((resolve, _) => {
                next_page.scrollIntoView();
                resolve();
            }).then(() => {
                let event = new Event('click', {
                    bubbles: true,
                    cancelable: true
                });
                next_page.dispatchEvent(event);
                callback();
            });
        } else {
            console.log("Something went wrong. The page options were not found")
        }
    });
}

