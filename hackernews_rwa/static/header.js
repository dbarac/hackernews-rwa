window.onload = initialize_site;

async function user_is_logged_in() {
	let url = "/api/sessions/";
	try {
		const response = await fetch(url, {
			method: 'GET'
		});
		const json = await response.json();
		return json;
	} catch (error) {
		console.log('Error: ', error);
	}
}

async function initialize_site() {
	let login_info = await user_is_logged_in();
	if (login_info.status == 'success') {
		//show logout link and tasks
		user_menu = document.getElementById("user-menu");
		user_menu.style.display = "initial";
		user_menu.querySelector("#uname").innerHTML = login_info.data.username;
		//tasks_div = document.getElementById("task-form");
		//tasks_div.style.display = "initial";
		//setup log out link
		logout_link = document.getElementById("logout-link");
		logout_link.addEventListener("click", function (event) {
			logout_user().then(() => {
				
			});
		});
	} else {
		//show log in and register links
		login_link = document.getElementById("login-link");
		login_link.style.display = "initial";

		register_link = document.getElementById("signup-link");
		register_link.style.display = "initial";
	}
}

//setup log out link
logout_link = document.getElementById("logout-link");
logout_link.addEventListener("click", function (event) {
	event.preventDefault(); 
	logout_user().then(() => {
		location.reload();
	});
});

async function logout_user() {
	let url = "/api/sessions/";
	try {
		const response = await fetch(url, {
			method: 'DELETE',
		});
	} catch (error) {
		console.log('Error: ', error);
	}
}

