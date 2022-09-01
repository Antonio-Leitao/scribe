<script>
    //necessary for all components:
    import { getContext } from "svelte";
    import Router, { location, link } from "svelte-spa-router";
  
    let content = getContext($location);
    let keys = [];
  
    for (let [key, value] of Object.entries(content)) {
      keys.push(key);
    }
  </script>
  
  <h1>
    This a {content.type} named {content.NAME}
  </h1>
  
  <h2>It has the following attritubes:</h2>
  
  {#each keys as key}
    <p>
      {key}
    </p>
  {/each}
  