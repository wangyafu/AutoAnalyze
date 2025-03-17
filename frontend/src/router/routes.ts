// 路由定义
import type{ RouteRecordRaw } from 'vue-router';
import WorkspaceView from '../views/WorkspaceView.vue';
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/workspace',
    name: 'workspace',
    component: WorkspaceView
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/SettingsView.vue')
  },
  {
    path: '/figure/:figureId',
    name: 'figure',
    component: () => import('../views/FigureView.vue'),
    props: true
  }
];

export default routes;