<script>
  //routing components
  import Router, { location, link } from "svelte-spa-router";
  import Home from "./routes/Home.svelte";
  import Name from "./routes/Name.svelte";
  import NotFound from "./routes/NotFound.svelte";
  import Wild from "./routes/Wild.svelte";
  import About from "./routes/About.svelte";
  import Blog from "./routes/Blog.svelte";

  //data
  export let content;
  //const routes = {};
  content['children'].forEach(child => {
    console.log(child['href']);
    //routes[child['href']]
  });


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

<hr />
{#each content['children'] as child }
<p>{child['href']}</p> 
{/each}
