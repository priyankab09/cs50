document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit', post_mail);
     
  // By default, load the inbox
    load_mailbox('inbox');
});



function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  get_emails(mailbox);
}

function post_mail() {
    
    const message = document.getElementById("message");
    message.innerHTML = '';

    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: document.querySelector('#compose-recipients').value,
            subject: document.querySelector('#compose-subject').value,
            body: document.querySelector('#compose-body').value
            })
        })
        .then(function (response) {
            if (response.status < 200 || response.status > 299) {
                return response.json()
            }
            load_mailbox('sent');
        })
       //.then(result => result.json())
        .then(result => {
            console.log(result.error);
            const msgresp = result.error;
            message.innerHTML = msgresp;           
        })
        .catch(error => {
            console.log(error);
        });


    return false;

}

function get_emails(mailbox) {

    console.log('getting emails for mailbox = ' + mailbox);
    fetch('/emails/' + mailbox)
        .then(response => response.json())
        .then(emails => {
            //emails.forEach(add_email, mailbox);
            for (let i = 0, len = emails.length; i < len; i++) {
                add_email(emails[i], mailbox);
            }
            
        });
}

function add_email(email, mailbox) {

    // Create new email
    //const emailrow = document.createElement('div');
    //emailrow.className = 'email_row';
    //emailrow.innerHTML = '<span class="sender">' + email.sender + '</span><span class="subject">' + email.subject + '</span><span class="timestamp">' + email.timestamp + '</span>'; 
    //document.querySelector('#emails-view').append(emailrow);

    //using template instead of above method of building the dom in code
    var template = document.querySelector('#email-container');

    // Clone the new row and insert it into the table
    var clone = template.content.cloneNode(true);
    var span = clone.querySelectorAll("span");
    span[0].textContent = email.sender;
    span[1].textContent = email.subject;
    span[2].textContent = email.timestamp;
    span[0].addEventListener('click', function () {
        console.log('This element has been clicked! for email id =' + email.id);
        view_email(email.id, mailbox);
    });
    span[1].addEventListener('click', function () {
        console.log('This element has been clicked! for email id =' + email.id);
        view_email(email.id, mailbox);
    });

    if (email.read) {
        clone.querySelectorAll('.email-row')[0].classList.add('email-read');
    }
    document.querySelector('#emails-view').append(clone);
   

}

function view_email(emailid, mailbox) {
    document.querySelector('#email-view').style.display = 'block';
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';

    let fetchedemail;

    fetch('/emails/' + emailid)
        .then(response => response.json())
        .then(email => {
            //console.log(email);
            document.querySelector('#view-sender').innerHTML = email.sender;
            document.querySelector('#view-recipient').innerHTML = email.recipients;
            document.querySelector('#view-subject').innerHTML = email.subject;
            document.querySelector('#view-timestamp').innerHTML = email.timestamp;
            document.querySelector('#view-body').innerHTML = email.body;
            if (email.read === false) { changeEmailStatus(emailid, 'read', true); }     
            fetchedemail = email;
        })
    const elemButton = document.querySelector('#archive-button');
    const replyButton = document.querySelector('#reply-button');    

    if (mailbox === 'inbox') {
        console.log("inbox mailbox - so adding Archive buttons");
        document.querySelector('#archive-button-container').style.display = 'block';        
        elemButton.innerText = 'Archive';
        
        elemButton.onclick = function () { changeEmailStatus(emailid, 'archive', true); };
        document.querySelector('#reply-button-container').style.display = 'block';
        replyButton.onclick = function () { reply_compose_email(fetchedemail); };
        
    }
    else if (mailbox === 'archive') {
        console.log("archive mailbox - so adding Unarchive buttons");
        document.querySelector('#archive-button-container').style.display = 'block';
        elemButton.innerText = 'Unarchive';
       
        console.log("attaching event in archive");
        elemButton.onclick = function () { changeEmailStatus(emailid, 'archive', false); };       
    }

    else {
        document.querySelector('#archive-button-container').style.display = 'none';
        document.querySelector('#reply-button-container').style.display = 'block';
        replyButton.onclick = function () { reply_compose_email(fetchedemail); };
    }
        
}        

function handleErrors(response) {

    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}


function changeEmailStatus(emailid, statusType, statusValue) {
    console.log("changeemailstatus called with " + statusType + emailid);

    let archive = false;

    let msgBody = '';
    if (statusType === 'read') {
        msgBody = JSON.stringify({ read: statusValue });
        console.log('changeemailstatus - marking read' + msgBody);
    } else if (statusType === 'archive') {
        msgBody = JSON.stringify({ archived: statusValue });
        archive = true;
        console.log('changeemailstatus - marking archived' + msgBody);
    } else {throw Error('Bad data when calling changeEmailStatus')}

    fetch('/emails/' + emailid, {
        method: 'PUT',
        body: msgBody
    })
    .then(handleErrors)
    .then(response => {
        console.log(response);
        if (archive) {
            load_mailbox('inbox');
        }
    })
    .catch(error => {
        console.log('Error:', error);
    });
}

function reply_compose_email(email) {

    const subject_reply_prefix = "Re:";

    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = email.sender;
    //document.querySelector('#compose-subject').value = 'Re: ' + email.subject;
    const subj = email.subject;

    document.querySelector('#compose-subject').value = (subj.slice(0,3) === subject_reply_prefix ? "" : subject_reply_prefix) + " " + subj;

    document.querySelector('#compose-body').value =  '\r\n\r\n' + 'On ' + ' ' + email.timestamp + ' ' + email.sender + ' wrote: ' + '\r\n\r\n' + email.body ;
}