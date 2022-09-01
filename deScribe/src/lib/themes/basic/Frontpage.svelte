<script>
  //necesary for all components:
  import { setContext } from "svelte";

  //routing components
  import Router, { location, link } from "svelte-spa-router";
  import Home from "./routes/Home.svelte";
  import Name from "./routes/Name.svelte";
  import NotFound from "./routes/NotFound.svelte";
  import Wild from "./routes/Wild.svelte";
  import Class from "./components/Class.svelte";
  import Function from "./components/Function.svelte";


  //capture content for funky fronpaage visualisations
  export let content;

  //drop json into Context so its acessible in other routes
  function cacheData(json) {
    setContext(json.href, json);

    if (json.hasOwnProperty("children")) {
      json.children.forEach((element) => {
        cacheData(element);
      });
    }
    return;
  }
  cacheData(content);
  

  //some other stuff
  function searchContent(obj, key) {
    let result = [];

    function findType(json, type) {
      if (json.type === type) {
        result.push(json);
      }

      if (json.hasOwnProperty("children")) {
        json.children.forEach((element) => {
          findType(element, type);
        });
      }
      return;
    }

    findType(obj, key);
    return result;
  }

  let classes = searchContent(content, "class");
  let routines = searchContent(content, "function");

  let routes = { "/": Home };
  classes.forEach((element) => {
    routes[element.href] = Class;
  });
  routines.forEach((element) => {
    routes[element.href] = Function;
  });
</script>

<nav>
  <a href="/">Home</a>
  {#each classes as clas}
    <a href={clas.href} use:link> {clas.NAME}</a>
  {/each}
  {#each routines as routine}
    <a href={routine.href} use:link> {routine.NAME}</a>
  {/each}
</nav>

<Router {routes} />

<!-- <nav>
  <a href="/">Home</a>
  <a href="/hello/svelte" use:link> Say hi!</a>
  <a href="/wild/card" use:link> Wildcard route</a>
  <a href="/does/not/exist" use:link> Not found</a>
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
/> -->

<div class="container">
  <nav>
    <ul>
      <li>
        <h2>CLASSES</h2>
        <ul>
          {#each classes as clas}
            <li>
              <a href={clas.href} use:link>{clas.NAME}</a>
            </li>
          {/each}
        </ul>
      </li>
      <li>
        <h2>DESIGN</h2>
        <ul>
          {#each routines as routine}
            <li>
              <a href={routine.href} use:link>{routine.NAME}</a>
            </li>
          {/each}
        </ul>
      </li>
    </ul>
  </nav>
</div>

<hr />
/#{$location}

<hr />
{#each content["children"] as child}
  <p>{child["href"]}</p>
  <p>{child["type"]}</p>
{/each}
