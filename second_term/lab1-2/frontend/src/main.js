import { createApp } from "vue";

import App from "./App.vue";
import { i18n, setI18nLocale } from "./i18n";
import { router } from "./router";
import { pinia } from "./stores";
import { useAppStore } from "./stores/app";
import { useAuthStore } from "./stores/auth";
import { installFormatting } from "./utils/formatting-plugin";
import "./styles/base.css";

const app = createApp(App);

app.use(pinia);

const appStore = useAppStore();
const authStore = useAuthStore();

appStore.initialize();
authStore.initialize();
setI18nLocale(appStore.language);

app.use(i18n);
app.use(router);
installFormatting(app);

app.mount("#app");
