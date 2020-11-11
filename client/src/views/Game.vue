<template>
  <div>
    <button @click="createGameWithFriend">test</button>
  </div>
</template>

<script>
import { mapActions } from "vuex";

export default {
  methods: {
    ...mapActions(["createGameWithFriend"])
  }
};
</script>
