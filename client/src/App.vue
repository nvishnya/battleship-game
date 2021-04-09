<template>
  <div id="app">
    <div id="background"></div>
    <div id="app-title">
      <span>battleship.</span>
    </div>
    <router-view />
  </div>
</template>

<script>
export default {
  mounted() {
    document.body.classList.add("theme-dark");
  }
};
</script>

<style lang="scss">
#id {
  background-color: transparent;
}
</style>
