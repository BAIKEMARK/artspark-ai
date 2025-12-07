<template>
  <footer id="footer-guide" :class="{ 'extra-margin': !isHomePage }">
    <div class="footer-content">
      <div class="footer-column">
        <h3>{{ $t('footer.guideTitle') }}</h3>
        <p>
          <strong>{{ $t('footer.teacherGuide') }}</strong> {{ $t('footer.teacherGuideText') }}
        </p>
      </div>
      <div class="footer-column">
        <h3>{{ $t('footer.resourcesTitle') }}</h3>
        <div style="display: flex; justify-content: space-between;">
          <div style="flex: 1; padding-right: 10px;">
            <h4>{{ $t('footer.domesticTitle') }}</h4>
            <ul>
              <li><a href="https://g2.ltfc.net/home" target="_blank">{{ $t('footer.museums.chinaHeritage') }}</a></li>
              <li><a href="https://www.namoc.cn/namoc/diancang/dc.shtml" target="_blank">{{ $t('footer.museums.namoc') }}</a></li>
              <li><a href="https://www.dpm.org.cn/lights/index.html" target="_blank">{{ $t('footer.museums.forbiddenCity') }}</a></li>
              <li><a href="https://www.cafamuseum.org/artist/collection" target="_blank">{{ $t('footer.museums.cafaMuseum') }}</a></li>
            </ul>
          </div>
          <div style="flex: 1; padding-left: 10px;">
            <h4>{{ $t('footer.internationalTitle') }}</h4>
            <ul>
              <li><a href="https://www.metmuseum.org/art/collection" target="_blank">{{ $t('footer.museums.metMuseum') }}</a></li>
              <li><a href="https://www.louvre.fr/en/departments/paintings/highlights" target="_blank">{{ $t('footer.museums.louvre') }}</a></li>
              <li><a href="https://www.nationalgallery.org.uk/paintings/search-the-collection" target="_blank">{{ $t('footer.museums.nationalGallery') }}</a></li>
              <li><a href="https://www.moma.org/collection/" target="_blank">{{ $t('footer.museums.moma') }}</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>{{ $t('footer.copyright') }}</p>
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
