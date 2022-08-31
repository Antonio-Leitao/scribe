<script>
  import Router, { location, link } from "svelte-spa-router";
  import Home from "./lib/themes/basic/routes/Home.svelte";
  import Name from "./lib/themes/basic/routes/Name.svelte";
  import NotFound from "./lib/themes/basic/routes/NotFound.svelte";
  import Wild from "./lib/themes/basic/routes/Wild.svelte";
  import About from "./lib/themes/basic/routes/About.svelte";
  import Blog from "./lib/themes/basic/routes/Blog.svelte";
</script>

<nav>
  <a href="/">Home</a>
  <a href="/#/hello/svelte">Say hi!</a>
  <a href="/#/wild/card">Wildcard route</a>
  <a href="/#/does/not/exist">Not found</a>
</nav>

<Router
  routes={{
    // Exact path
    "/": Home,

    // Using named parameters, with last being optional
    "/hello/:first/:last?": Name,

    // Wildcard parameter
    // Included twice to match both `/wild` (and nothing after) and `/wild/*` (with anything after)
    "/wild": Wild,
    "/wild/*": Wild,

    // Catch-all, must be last
    "*": NotFound,
  }}
/>

<hr />
/#{$location}
