document$.subscribe(({ body }) => {
	const content = body.querySelector('.md-content');

	content
		.querySelectorAll('h1, h2, h3, h4, h5, h6')
		.forEach(e => e.classList.add('text-topic'));

	content.querySelectorAll('p, ol, ul')
		.forEach(e => e.classList.add('text-content'));
});
