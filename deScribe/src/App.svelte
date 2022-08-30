<script>
	import Router, {location, link} from 'svelte-spa-router';
	import Home from './lib/themes/basic/Home.svelte';
	import About from './lib/themes/basic/About.svelte';
	import Blog from './lib/themes/basic/Blog.svelte';
</script>

<nav>
	<a  href="/">Home</a>
	<a href="/#/about">About</a>
	<a href="/#/blog/colors">Colors</a>
</nav>

<Router routes={{
	'/': Home,
	'/about': About,
	'/blog/:blogName': Blog
}} />

<hr>
/#{$location}