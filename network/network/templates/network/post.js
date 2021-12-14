// JavaScript source code
document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('#all-posts').addEventListener('click', () => load_posts('all'));
    document.querySelector('#following-posts').addEventListener('click', () => load_posts('following'));
    document.querySelector('#post-form').addEventListener('submit', post_content);
    //document.querySelector('#post-form').addEventListener('submit', () => load_posts('all'));
    alert('loaded');
    load_posts('all');
});

function load_posts(these_posts) {
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#new-post').style.display = 'block';
    document.querySelector('#profile-view').style.display = 'none';
}

function load_profile(userid, these_posts) {
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#new-post').style.display = 'none';
    document.querySelector('#profile-view').style.display = 'none'
}

function post_content() {
    alert('called');
    fetch('posts', {
        method: 'POST', 
        body: JSON.stringify({
            content: document.querySelector('#post-content').value
        })
    })
        .then(handleErrors)
        .then(response => response.json())
        .then(result => {
            load_posts('all');
        })
        .catch(error => {
            console.log('Error:', error);
        });

    return false;

}

   // .then(response => response.json())
   // .then(post => {
   //     document.querySelector('#post-user') = post.user;
   //     document.querySelector('#post-content') = post.content;
   //     document.querySelector('#post-')

function get_posts(these_posts) {
    fetch('posts/' + these_posts)
        .then(response => response.json())
        .then(posts => {
            for (let i = 0, len = posts.length; i < len; i++) {
                add_post(posts[i], these_posts);
            }
        });
}

function add_post(post, these_posts) {
    var template = document.querySelector('#post-container');

    //template.innerHTML = template.innerHTML.replace("#emailid", email.id);
    // Clone the new row and insert it into the table
    var clone = template.content.cloneNode(true);
    var span = clone.querySelectorAll("div");
    span[0].textContent = post.user;
    span[1].textContent = post.content;
    span[2].textContent = post.timestamp;
    span[0].addEventListener('click', function () {
        console.log('This element has been clicked! for email id =' + email.id);
        view_email(email.id, mailbox);
    });
    span[1].addEventListener('click', function () {
        console.log('This element has been clicked! for email id =' + email.id);
        view_email(email.id, mailbox);
    });
}

function edit_post (postid, el) {
    alert(el.name + ' ' + postid);
}

function edit_post2(postid) {
    alert(postid);
}

function get_followers() {

}

function handleErrors(response) {

    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}




