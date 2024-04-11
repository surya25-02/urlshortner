document.getElementById('username')?.addEventListener('input', signup_validation);
document.getElementById('password')?.addEventListener('input', signup_validation);
document.getElementById('confirmpassword')?.addEventListener('input', signup_validation);
document.getElementById('shorten')?.addEventListener('click', shortlink);
document.querySelectorAll('#removebutton').forEach(i => {
    i.addEventListener('click', remove_shortlink);
})


async function sleep(seconds) {
    return new Promise(reslove => setTimeout(reslove, seconds * 1000));
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

    const [body] = document.getElementsByTagName('body');

    if (['Login Page', 'SignUp',].includes(document.title)) {
        body.style.backgroundColor = '#1d2a35'
    }
}

function copy_text_to_clipboard(element) {
    const text = element.getAttribute('data-clipboard-target')
    navigator.clipboard.writeText(text)
}

async function signup_validation() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const cpassword = document.getElementById('confirmpassword').value;
    const button = document.getElementById('formbutton');
    button.disabled = true;

    if (/[^A-Z0-9_]/i.test(username)) {
        document.getElementById('usernamehelptext').classList.remove('d-none');
    } else {
        document.getElementById('usernamehelptext').classList.add('d-none');
    }

    if (password !== cpassword) {
        document.getElementById('passwordhelptext').classList.remove('d-none');
    } else {
        document.getElementById('passwordhelptext').classList.add('d-none');
        if (!/[^A-Z0-9_]/i.test(username)) {
            button.disabled = false;
        }
    }
}

async function showpassword() {
    const password = document.querySelector('[name=password]');
    password.type == 'password' ? password.type = 'text' : password.type = 'password';

    if (document.title === 'Login Page') {
        const icon = document.getElementById('eye');
        icon.className = icon.className === "fa-solid fa-eye-slash" ? "fa-solid fa-eye" : "fa-solid fa-eye-slash";
    } else {
        const cpassword = document.getElementById('confirmpassword');
        cpassword.type = cpassword.type === 'password' ? 'text' : 'password';
    }
}

async function shortlink() {
    const url_input_box = document.getElementById('url_input_box');
    const long_url = url_input_box.value;

    if (!long_url) {
        alert('Enter the URL first')
        return;
    }

    this.classList.add('clicked')
    this.innerHTML = `<i class="fa-solid fa-rotate fa-spin fa-lg"></i>`;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const form = new FormData();
    form.append('long_url', long_url)
    form.append('csrfmiddlewaretoken', csrftoken)

    const res = await fetch('/api/shortlink', {
        method: 'POST',
        body: form,
    })

    if ([401, 403].includes(res.status)) {
        return window.location.href = '/login'
    }

    const { shorten_link } = await res.json();
    this.innerHTML = `<i class="fa-solid fa-check"></i>`;
    await sleep(1)
    const inputgroup = document.getElementById('change');

    if (document.title === 'Dashboared') {
        url_input_box.value = shorten_link;
        this.innerHTML = 'SHORT';
        return;
    }

    inputgroup.innerHTML = `<input type="text" class="form-control p-3 border-0" id="url_input_box" value="${shorten_link}" style="box-shadow: none;" readonly>
    <button class="btn btn-light" type="button" id="copy" data-clipboard-target="${shorten_link}"><i class="fa-regular fa-copy"></i></button>
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
                <input type="text" class="form-control p-3 border-0" id="url_input_box" placeholder="your url here" style="box-shadow: none;" required>
                <button class="btn btn-light fw-bold" type="submit" id="shorten">Shorten</button>`;
                document.getElementById('shorten')?.addEventListener('click', shortlink)
                await sleep(1)
                instance.hide();
            })
        }
    });

}

async function remove_shortlink() {
    const newElement = document.createElement("div");
    newElement.className = "spinner-border text-danger"
    newElement.role = "status"
    this.parentNode.replaceChild(newElement, this);
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const res = await fetch(`/api/shortlink?url=${this.value}`,
        {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        }
    )

    if (res.status === 204) {
        location.reload(true);
    }
}
