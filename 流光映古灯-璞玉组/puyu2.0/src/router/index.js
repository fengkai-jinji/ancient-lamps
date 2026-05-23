import { createRouter, createWebHashHistory } from 'vue-router';
import Home from '../views/home/index.vue';
import Chose from '../views/Chose/index.vue';
import History from '../views/history/index.vue';
import Map from '../views/map/index.vue';
import Card from '../views/card/index.vue';
import Culture from '../views/culture/index.vue';
import Modern from '../views/modern/index.vue';
import AIChatView from '../views/modern/AIChatView.vue';
import DesignPrintView from '../views/modern/DesignPrintView.vue';
import VirtualLampAnimation from '../views/modern/VirtualLampAnimation.vue';
import NotFind from '../views/Notfind.vue';

const router = createRouter({
  history: createWebHashHistory(),
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0, behavior: 'smooth' };
    }
  },
  linkActiveClass: 'router-link-active',
  linkExactActiveClass: 'router-link-exact-active',
  routes: [
    {
      path: '/',
      name: 'chose',
      redirect: '/home',
      component: Chose,
      children: [
        {
          path: '/home',
          name: 'Home',
          component: Home,
          meta: { title: '首页 - 流光映古灯', transitionName: 'fade-slide' }
        },
        {
          path: '/card',
          name: 'card',
          component: Card,
          meta: { title: '灯具鉴赏 - 流光映古灯', transitionName: 'fade-slide' }
        },
        {
          path: '/history',
          name: 'history',
          component: History,
          meta: { title: '灯史长河 - 流光映古灯', transitionName: 'fade-slide' }
        },
        {
          path: '/culture',
          name: 'culture',
          component: Culture,
          meta: { title: '文化内涵 - 流光映古灯', transitionName: 'fade-slide' }
        },
        {
          path: '/map',
          component: Map,
          meta: { title: '地域灯踪 - 流光映古灯', transitionName: 'fade-slide' }
        },
        {
          path: '/modern',
          name: 'modern',
          component: Modern,
          meta: { title: '今夕共赏 - 流光映古灯', transitionName: 'fade-slide' },
          children: [
            {
              path: 'ai-chat',
              name: 'ai-chat',
              component: AIChatView,
              meta: { title: 'AI对话 - 流光映古灯', transitionName: 'fade-slide' }
            },
            {
              path: 'design-print',
              name: 'design-print',
              component: DesignPrintView,
              meta: { title: '设计打印 - 流光映古灯', transitionName: 'fade-slide' }
            },
            {
              path: 'virtual-lamp-animation',
              name: 'virtual-lamp-animation',
              component: VirtualLampAnimation,
              meta: { title: '古灯动画 - 流光映古灯', transitionName: 'fade-slide' }
            }
          ]
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      component: NotFind,
      meta: { title: '页面未找到 - 流光映古灯', transitionName: 'fade' }
    }
  ]
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '流光映古灯';
  next();
});

export default router;