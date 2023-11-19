document.getElementById('username')?.addEventListener('input', check1);
document.getElementById('password')?.addEventListener('input', check1);
document.getElementById('confirmpassword')?.addEventListener('input', check1);
document.getElementById('shorten')?.addEventListener('click', shortlink);
document.querySelectorAll('#removebutton').forEach(i => {
    i.addEventListener('click', remove_shortLink);
})


async function sleep(seconds) {
    return await new Promise( reslove => {
        setTimeout(reslove, seconds * 1000)
    })
}

window.onload = function winload() {
    
    tippy('[data-tippy-content]', {
        hideOnClick: false,
        theme: 'black',
        placement: 'left',
        onShow(instance) {
            instance.reference.addEventListener('click', async () => {
                copy_text_to_clipboard(instance.reference)
                instance.setContent('Copied')
                await sleep(1)
                instance.hide();
            })
        }
    });
    let title = document.title;
    body = document.getElementsByTagName('body');
    if (['Login Page', 'SignUp', ].includes(title)) {
        body[0].style.backgroundColor = '#1d2a35'        
    } 
}

function copy_text_to_clipboard(element) {

    let text = element.getAttribute('data-clipboard-target')
    navigator.clipboard.writeText(text)
    
}

function check1() {
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    let cpassword = document.getElementById('confirmpassword').value;
    let button = document.getElementById('formbutton');
    let disabled = false;
    if (/[^A-Z0-9_]/i.test(username.trim())) {
        document.getElementById('usernamehelptext').classList.remove('d-none');
        button.disabled = true;
        disabled = true;
    } else {
        document.getElementById('usernamehelptext').classList.add('d-none');
        button.disabled = false;
        disabled = false;
    }
    if (password.length > 0 && cpassword.length > 0 && password != cpassword) {
        document.getElementById('passwordhelptext').classList.remove('d-none');
        button.disabled = true;
    } else {
        document.getElementById('passwordhelptext').classList.add('d-none');
        if (!disabled) button.disabled = false;
    }

}

async function showpassword() {
    let password = document.querySelector('[name=password]');
    let cpassword = document.getElementById('confirmpassword');
    if (password) {
        password.type == 'password' ? password.type = 'text' : password.type = 'password';
        let icon = document.getElementById('eye');
        if (icon) {
            icon.className == "fa-solid fa-eye-slash" ? icon.className = "fa-solid fa-eye" : icon.className = "fa-solid fa-eye-slash";
        }
    }
    if (cpassword) {
        cpassword.type == 'password' ? cpassword.type = 'text' : cpassword.type = 'password';
    }
}

async function shortlink() {
    let button = this;
    button.classList.add('clicked')
    button.innerHTML = `<i class="fa-solid fa-rotate fa-spin fa-lg"></i>`;
    
    let url = document.getElementById('url');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let form = new FormData();
    form.append('long_url', url.value)
    form.append('csrfmiddlewaretoken', csrftoken)
    let res = await fetch('/api/shortlink', {
        method: 'POST',
        body: form,
    });
    if ([401, 403].includes(res.status)) {
        return window.location.href = '/login'
    }
    res = await res.json()

    button.innerHTML = `<i class="fa-solid fa-check"></i>`;
    await sleep(1)

    let inputgroup = document.getElementById('change');

    let link = res.shorten_link

    if (document.title === 'Dashboared') {
        url.value = link
        button.innerHTML = 'SHORT'
        return
    }
   
    inputgroup.innerHTML = `<input type="text" class="form-control p-3 border-0" id="url" value="${link}" style="box-shadow: none;" readonly>
    <button class="btn btn-light" type="button" id="copy" data-clipboard-target="${link}"><i class="fa-regular fa-copy"></i></button>
    <button class="btn btn-light" type="button" id="reshort"><i class="fa-solid fa-rotate"></i></button>
    `

    tippy('#copy', {
        theme: 'black',
        content: 'Copy',
        placement: 'bottom',
        arrow: true,
        theme: 'black',
        onShow(instance) {
            instance.reference.addEventListener('click', async () => {
                copy_text_to_clipboard(instance.reference)
                instance.setContent('Copied')
                await sleep(1)
                instance.hide();
            })
        }
    })
    

    tippy('#reshort', {
        theme: 'black',
        content: 'Reshort',
        placement: 'bottom',
        arrow: true,
        onShow(instance) {
            instance.reference.addEventListener('click', async () => {
                inputgroup.innerHTML = `
                <input type="text" class="form-control p-3 border-0" id="url" placeholder="your url here" style="box-shadow: none;" required>
                <button class="btn btn-light fw-bold" type="submit" id="shorten">Shorten</button>`;
                await sleep(1)
                instance.hide();
            })
        }
    });

}

async function remove_shortLink(){
    let button = this;
    var newElement = document.createElement("div");
    newElement.className = "spinner-border text-danger"
    newElement.role = "status"
    button.parentNode.replaceChild(newElement, button);
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    res = await fetch(`${location.origin}/api/shortlink?url=${button.value}`,
        {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        }
    )
    if (res.status == 204){
        location.reload(true);
    }
}
