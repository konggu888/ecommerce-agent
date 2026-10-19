<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchApiHealth, type ApiConnectionState } from "./api";

const learnerName = ref("小小数学家");
const showWelcome = ref(true);
const apiState = ref<ApiConnectionState>({ status: "checking" });

onMounted(async () => {
  try {
    const health = await fetchApiHealth();
    apiState.value = { status: "connected", health };
  } catch (error) {
    apiState.value = {
      status: "unavailable",
      message: error instanceof Error ? error.message : "暂时无法连接服务",
    };
  }
});
</script>

<template>
  <main class="page-shell">
    <header class="topbar">
      <a class="brand" href="/" aria-label="数学小老师首页"><span class="brand-mark">数</span><span>数学小老师</span></a>
      <span class="topbar-note">每天一点点，学会真本领</span>
    </header>

    <section class="welcome-card" aria-labelledby="welcome-title">
      <div class="welcome-copy">
        <p class="eyebrow">今天也可以慢慢来</p>
        <h1 id="welcome-title">你好，{{ learnerName }}！<br /><span>准备好探索数学了吗？</span></h1>
        <p class="intro">不着急，也不比快。我们一起想一想、画一画，再由你自己试试看。</p>
        <button class="primary-button" type="button" @click="showWelcome = !showWelcome">
          {{ showWelcome ? "看看今天怎么学" : "回到欢迎页" }} <span aria-hidden="true">→</span>
        </button>
      </div>
      <div class="teacher-card" aria-label="AI 数学老师正在等待你">
        <div class="teacher-orbit orbit-one"></div><div class="teacher-orbit orbit-two"></div>
        <div class="teacher-avatar" aria-hidden="true"><span class="teacher-hair"></span><span class="teacher-face"><i class="eye eye-left"></i><i class="eye eye-right"></i><i class="smile"></i></span><span class="teacher-body"></span></div>
        <div class="teacher-status"><span class="status-dot"></span> 数学老师在这里</div>
      </div>
    </section>

    <section v-if="showWelcome" class="content-grid" aria-label="学习入口">
      <article class="learning-card unit-card"><div class="card-icon" aria-hidden="true">✎</div><div><p class="card-kicker">自主练习</p><h2>我想练一练</h2><p>自己选择单元和题目，想停就停。</p></div><button class="text-button" type="button" disabled>即将开放</button></article>
      <article class="learning-card photo-card"><div class="card-icon" aria-hidden="true">▧</div><div><p class="card-kicker">试卷小帮手</p><h2>看看我的试卷</h2><p>一起看清题目，再决定从哪里开始。</p></div><button class="text-button" type="button" disabled>即将开放</button></article>
    </section>

    <section v-else class="next-step" aria-live="polite"><span class="step-number">01</span><div><h2>先选一个你想了解的数学单元</h2><p>完整学习功能正在建设中。现在不会记录练习或伪造学习成绩。</p></div></section>

    <footer class="page-footer">
      <span>认真思考，比答得快更重要。</span>
      <span v-if="apiState.status === 'checking'" role="status" data-testid="api-status">正在连接学习服务…</span>
      <span v-else-if="apiState.status === 'connected'" role="status" data-testid="api-status">学习服务已连接 · {{ apiState.health.storage }} 数据层</span>
      <span v-else role="status" data-testid="api-status" :title="apiState.message">学习服务暂不可用，当前页面不会保存学习记录</span>
      <span>当前为开发基线页面 · 学习记录功能尚未启用</span>
    </footer>
  </main>
</template>
