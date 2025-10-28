<template>
  <footer id="footer-guide" :class="{ 'extra-margin': !isHomePage }">
    <div class="footer-content">
      <div class="footer-column">
        <h3>使用指南和教学建议</h3>
        <p>
          <strong>教师指南：</strong> 可使用“AI智能上色”让学生练习色彩搭配。使用“创意风格工坊”和“AI自画像”激发学生的创造力和想象力。“艺术知识问答”可作为课堂小百科使用。新增的“名画鉴赏室”可用于名作赏析课。
        </p>
      </div>
      <div class="footer-column">
        <h3>艺术资源</h3>
        <div style="display: flex; justify-content: space-between;">
          <div style="flex: 1; padding-right: 10px;">
            <h4>国内</h4>
            <ul>
              <li><a href="https://g2.ltfc.net/home" target="_blank">中华珍宝馆</a></li>
              <li><a href="https://www.namoc.cn/namoc/diancang/dc.shtml" target="_blank">典藏-中国美术馆</a></li>
              <li><a href="https://www.dpm.org.cn/lights/index.html" target="_blank">故宫博物院</a></li>
              <li><a href="https://www.cafamuseum.org/artist/collection" target="_blank">中央美术学院美术馆</a></li>
            </ul>
          </div>
          <div style="flex: 1; padding-left: 10px;">
            <h4>国外</h4>
            <ul>
              <li><a href="https://www.metmuseum.org/art/collection" target="_blank">大都会艺术博物馆</a></li>
              <li><a href="https://www.louvre.fr/en/departments/paintings/highlights" target="_blank">卢浮宫博物馆</a></li>
              <li><a href="https://www.nationalgallery.org.uk/paintings/search-the-collection" target="_blank">英国国家美术馆</a></li>
              <li><a href="https://www.moma.org/collection/" target="_blank">纽约现代艺术博物馆 (MoMA)</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© 2025 艺启智AI - 智能美术助教项目</p>
    </div>
  </footer>
</template>

<script setup>
defineProps({
  isHomePage: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
footer { width: 100%; background: var(--secondary-color); color: rgba(255, 255, 255, 0.7); padding: 0; margin-top: auto; flex-shrink: 0; }
.footer-content { max-width: 900px; margin: 0 auto; padding: 0.5rem 1.5rem; display: flex; flex-wrap: wrap; gap: 20px; }
.footer-column { flex: 1; min-width: 300px; }
.footer-column h3 { color: white; font-family: var(--font-serif); font-weight: 600; border-bottom: 1px solid var(--accent-color); padding-bottom: 10px; }
.footer-column h4 { margin-top: 5px; margin-bottom: 5px; }
.footer-column p, .footer-column li { font-size: 0.9rem; line-height: 1.8; }
.footer-column ul { list-style: none; padding: 0; }
.footer-column a { color: rgba(255, 255, 255, 0.9); text-decoration: none; transition: color 0.3s ease; }
.footer-column a:hover { color: white; text-decoration: underline; }
.footer-bottom { background: rgba(0, 0, 0, 0.06); padding: 0.25rem; text-align: center; font-size: 0.85rem;}
.footer-bottom p {margin: 0;}
#footer-guide.extra-margin {margin-top: 2rem;}
</style>
