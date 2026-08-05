import "./shared/assets/styles/variables.css";
import "./shared/assets/styles/theme.css";
import "./assets/main.css";

import {
  createApp,
} from "vue";

import {
  createPinia,
} from "pinia";

import App from "./App.vue";
import router from "./router";

createApp(App)
  .use(createPinia())
  .use(router)
  .mount("#app");
