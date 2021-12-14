document.addEventListener('DOMContentLoaded', function () {
    
    const editpost = document.querySelectorAll('.like_toggle');
    editpost.forEach(function (el) {
        el.addEventListener('click', update_likes_count);
    });

});

//Used in index.html and profile.html for the edit post requirement. 
//Because in two places, created following funciton to be called from each html page
function SetEditPostClickEventListener() {

    const editpost = document.querySelectorAll('.edit_post');
    editpost.forEach(function (el) {
        el.addEventListener('click', edit_post);
    });
}

//Function to help enable or disable the post button if the text element has text or is empty respt.
function can_post(el_text, el_button) {
    if (el_text.value.trim() === "") {
        el_button.disabled = true;
    } else {
        el_button.disabled = false;
    }
}

//reference - https://docs.djangoproject.com/en/3.2/ref/csrf/
//get cookie by name.  Borrowed from above reference site. 
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function load_posts(these_posts) {
    get_posts(these_posts);
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#new-post').style.display = 'block';
}

function load_profile(userid, these_posts) {
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#new-post').style.display = 'none';
}

function post_content() {
    
    fetch('/post', {
        method: 'POST', 
        body: JSON.stringify({
            content: document.querySelector('#post-content').value
        })
    })
        .then(handleErrors)
        .then(response => response.json())
        .then(result => {
            console.log(result);
            load_posts('all');
        })
        .catch(error => {
            console.log('Error:', error);
        });

    return false;

}


function get_posts(these_posts) {
    if (these_posts === 'all') { these_posts = ''; } else { these_posts = '/' + these_posts; }
    console.log('these_posts' + these_posts);
    fetch('/posts')
        .then(response => response.json())
        .then(posts => {
            for (let i = 0, len = posts.length; i < len; i++) {
                add_post(posts[i], these_posts);
            }
        });
}

function update_likes_count(event) {

    const el = event.target;
    let postid = el.dataset.pid;
    console.log(el.name + ' ' + postid);
    const el_post = el.closest('.post');
    const el_likes_count = el_post.querySelector(".likes_count");
    console.log('like count' + ' ' + el_likes_count.textContent);
    
    fetch('/like_update/' + postid, {
        method: 'POST'
    })
        .then(handleErrors)
        .then(response => response.json())
        .then(result => {
            console.log(result.likes);
            el_likes_count.textContent = result.likes;
        })
        .catch(error => {
            console.log('Error:', error);
        });
}

function add_post(post, these_posts) {

    var template = document.querySelector('#post-container');
    var clone = template.content.cloneNode(true);
    var div = clone.querySelectorAll("div");
    div[1].innerHTML ='<a href="/index/' + post.poster_id + '">' + post.poster + '</a>';
    div[2].textContent = post.content;
    div[3].textContent = post.created_at;
    document.querySelector('#posts').append(clone);
}
  
function save_post_changes(event) {
    let el = event.target;

    let updpostid = el.dataset.pid;
    const el_post = el.closest('.post');
    const el_content = el_post.querySelector(".content");
    const el_likes_count = el_post.querySelector(".likes_count");
    const el_content_edit = el_post.querySelector(".content_edit");
    const el_content_edit_val = el_content_edit.getElementsByTagName('textarea')[0].value;
    const newtext = el_content_edit_val.trim();

    //for security, we use a token to ensure that only the logged in user can update own message
    const csrft = getCookie("csrftoken"); 
    
    fetch('/post_update', {
        method: 'PUT',
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": csrft
        },
        body: JSON.stringify({
            postid: updpostid,
            content: newtext
        })
    })

        .then(handleErrors)
        .then(response => response.json())
        .then(result => {

            el_content.textContent = result.content;
            el_likes_count.textContent = result.likes_count;
            el_content_edit.getElementsByTagName('textarea')[0].remove;
            el_content_edit.innerHTML = '';
            el_content.style.display = 'inline'; //setting it to 'none' retained space

            el.textContent = "Edit";
            el.classList.remove('btn-primary');
            el.classList.add('btn-link');
            el.removeEventListener("click", save_post_changes);
            el.addEventListener("click", edit_post);
        })
        .catch(error => {
            console.log('Error:', error);
        });
}
        
function edit_post(event) {

    const el = event.target;

    let postid = el.dataset.pid;

    const el_post = el.closest('.post');
    const el_content = el_post.querySelector(".content");
    const el_content_edit = el_post.querySelector(".content_edit");

    let content_text = el_content.textContent;
    const content_textarea = document.createElement("textarea");
    content_textarea.maxLength = 255;
    content_textarea.rows = 2;
    content_textarea.cols = 150;

    content_textarea.textContent = content_text;
    el_content.style.display = 'none';
    el_content_edit.append(content_textarea);

    //Give Save link the standard button look
    el.textContent = "Save";
    el.removeEventListener("click", edit_post);
    el.classList.remove('btn-link');
    el.classList.add('btn-primary');

    //add event listener to disable button if no text has been entered
    content_textarea.addEventListener('keyup', function () { can_post(content_textarea, el); });

    el.addEventListener("click", save_post_changes);

}


function handleErrors(response) {

    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}




