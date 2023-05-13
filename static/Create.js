const form = document.querySelector("form");
const urlInput = document.querySelector("#url");
const shortInput = document.querySelector("#short");
const message = document.querySelector("#message");
const shortenBtn = document.querySelector("#shorten-btn");

form.addEventListener("submit", async (event) => {
	event.preventDefault();

	const url = urlInput.value;
	const short = shortInput.value;

	const urlRegex =
		/https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)/;
	if (!urlRegex.test(url)) {
		message.innerHTML = "❌ Invalid URL";
		return;
	}

	const response = await fetch("/create", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			url: url,
			short: short,
		}),
	});

	const data = await response.json();
	if (data.error) {
		message.innerHTML = "❌ " + data.error;
	} else {
		message.innerHTML =
			"✅ Your short URL is: " +
			`<a target="_blank" href='` +
			data.short +
			"'>" +
			data.short +
			"</a>";
	}
});
