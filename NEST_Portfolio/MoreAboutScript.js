function wait_for_description(article, filter_bar, article_name, callback) {
    console.log("Inside wait_for_description")
    const button = article.querySelector('.ALT-01 ');
    let event = new Event('click', {
        bubbles: true,
        cancelable: true
    });
    console.log("Button description: ", button.textContent);

    const modal_content = filter_bar.querySelector('.modal-content');
    const old_description = modal_content.querySelector('p').textContent;

    button.dispatchEvent(event);

    new Promise((resolve, _) => {
        let intervalId = setInterval(() => {
            console.log("Checking for new description")
            const new_description = modal_content.querySelector('p').textContent;
            console.log(new_description)
            if (new_description !== old_description || (new_description === old_description && window['last_article_name'] === article_name)) {
                clearInterval(intervalId);
                resolve(new_description);
            }
        }, 2000);
    }).then((new_description) => {
        console.log("New Description: ", new_description);
        window['last_article_name'] = article_name
        callback(new_description);
    });

}

function compare_names(name, article_name) {
    if (name.length !== article_name.length) {
        return false;
    } else {
        for (let i = 0; i < name.length; i++) {
            if (name[i] !== article_name[i]) {
                return false;
            }
        }
        return true;
    }
}

function get_more_about(article_index, article_name,  callback) {
    console.log("Inside get_more_about");
    const filter_bar = document.querySelector('.filterbar');
    const articles = filter_bar.querySelectorAll('article');
    const article = articles[article_index];
    const name = article.querySelector('.name');
    // console.log("Name is: ", name.textContent, " and article_name is: ", article_name)

    if (compare_names(name.textContent, article_name)) {
        console.log(article_name)
        wait_for_description(article, filter_bar, article_name, callback);
    } else {
        for (let article of articles) {
            const name = article.querySelector('.name');
            if (name.getAttribute('textContent') === article_name) {
                wait_for_description(article, filter_bar, name, callback);
            }
        }
    }
}