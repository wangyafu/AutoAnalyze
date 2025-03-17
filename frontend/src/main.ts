import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import "./assets/tailwind.css"
const app = createApp(App)

// 使用Pinia状态管理
app.use(pinia)
app.use(ElementPlus)
// 使用Vue Router
app.use(router)

app.mount('#app')
