import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import axios from "axios";
import VueAxios from "vue-axios";
import Clipboard from "v-clipboard";

Vue.config.productionTip = false;
Vue.use(VueAxios, axios);
Vue.use(Clipboard);

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
