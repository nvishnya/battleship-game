<template>
  <div id="app">
    <div id="app-title">
      <span>battleship.</span>
    </div>
    <router-view />
  </div>
</template>

<script>
export default {
  mounted() {
    document.documentElement.classList.add("theme-dark");
  }
};
</script>

<style lang="scss">
#id {
  background-color: transparent;
}
</style>
