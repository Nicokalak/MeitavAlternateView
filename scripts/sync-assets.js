import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_DIR = path.resolve(__dirname, '..');
const NODE_MODULES = path.join(ROOT_DIR, 'node_modules');
const STATIC_DIR = path.join(ROOT_DIR, 'src', 'meitav_view', 'static');

const ASSET_MAPPINGS = [
  // CSS
  { src: 'bootstrap/dist/css/bootstrap.min.css', dest: 'css/bootstrap.min.css' },
  { src: 'bootstrap-icons/font/bootstrap-icons.css', dest: 'css/bootstrap-icons.css' },
  { src: 'bootstrap-icons/font/fonts/bootstrap-icons.woff', dest: 'css/fonts/bootstrap-icons.woff' },
  { src: 'bootstrap-icons/font/fonts/bootstrap-icons.woff2', dest: 'css/fonts/bootstrap-icons.woff2' },
  { src: '@fortawesome/fontawesome-free/css/all.min.css', dest: 'css/all.min.css' },
  { src: 'bootstrap-table/dist/bootstrap-table.min.css', dest: 'css/bootstrap-table.min.css' },
  
  // JS
  { src: 'jquery/dist/jquery.min.js', dest: 'js/jquery.min.js' },
  { src: '@popperjs/core/dist/umd/popper.min.js', dest: 'js/popper.js' },
  { src: 'bootstrap/dist/js/bootstrap.bundle.min.js', dest: 'js/bootstrap.bundle.min.js' },
  { src: 'bootstrap-table/dist/bootstrap-table.min.js', dest: 'js/bootstrap-table.min.js' },
  { src: 'bootstrap-table/dist/extensions/auto-refresh/bootstrap-table-auto-refresh.min.js', dest: 'js/bootstrap-table-auto-refresh.min.js' },
  { src: 'bootstrap-table/dist/extensions/export/bootstrap-table-export.min.js', dest: 'js/bootstrap-table-export.min.js' },
  { src: 'tableexport.jquery.plugin/tableExport.min.js', dest: 'js/tableExport.min.js' },
  { src: 'xlsx/dist/xlsx.full.min.js', dest: 'js/xlsx.full.min.js' },
  { src: 'chart.js/dist/chart.umd.js', dest: 'js/chart.umd.min.js' },
  { src: 'chartjs-adapter-moment/dist/chartjs-adapter-moment.min.js', dest: 'js/chartjs-adapter-moment.min.js' },
  { src: 'moment/min/moment-with-locales.min.js', dest: 'js/moment-with-locales.min.js' },
];

const WEBFONTS_DIR = path.join(NODE_MODULES, '@fortawesome', 'fontawesome-free', 'webfonts');
const WEBFONTS_DEST = path.join(STATIC_DIR, 'webfonts');

function copyAssets() {
  console.log('Copying static assets from node_modules...');

  ASSET_MAPPINGS.forEach(({ src, dest }) => {
    const srcPath = path.join(NODE_MODULES, src);
    const destPath = path.join(STATIC_DIR, dest);

    if (fs.existsSync(srcPath)) {
      fs.mkdirSync(path.dirname(destPath), { recursive: true });
      fs.copyFileSync(srcPath, destPath);
      console.log(`  Copied: ${src} -> ${dest}`);
    } else {
      console.warn(`  Warning: Source asset not found: ${srcPath}`);
    }
  });

  // Copy FontAwesome webfonts
  if (fs.existsSync(WEBFONTS_DIR)) {
    fs.mkdirSync(WEBFONTS_DEST, { recursive: true });
    const fonts = fs.readdirSync(WEBFONTS_DIR);
    fonts.forEach((font) => {
      fs.copyFileSync(path.join(WEBFONTS_DIR, font), path.join(WEBFONTS_DEST, font));
    });
    console.log(`  Copied ${fonts.length} webfonts.`);
  }
}

function updateIndexIntegrityHashes() {
  const indexPath = path.join(STATIC_DIR, 'index.html');
  if (!fs.existsSync(indexPath)) return;

  let htmlContent = fs.readFileSync(indexPath, 'utf-8');
  console.log('Updating index.html Subresource Integrity (SRI) hashes...');

  // Update <link> and <script> tags with integrity attribute
  const linkAndScriptRegex = /(<(?:link|script)\s+[^>]*?(?:href|src)=["']([^"']+)["'][^>]*?>)/gi;

  htmlContent = htmlContent.replace(linkAndScriptRegex, (match, tag, assetPath) => {
    // Only update if tag contains integrity attribute
    if (!tag.includes('integrity=')) {
      return match;
    }

    const cleanPath = assetPath.split('?')[0];
    const fullAssetPath = path.join(STATIC_DIR, cleanPath);

    if (fs.existsSync(fullAssetPath)) {
      const fileBuffer = fs.readFileSync(fullAssetPath);
      const hash = crypto.createHash('sha384').update(fileBuffer).digest('base64');
      const newIntegrity = `sha384-${hash}`;

      const updatedTag = tag.replace(/integrity=["'][^"']+["']/, `integrity="${newIntegrity}"`);
      console.log(`  Updated SRI for ${cleanPath}: ${newIntegrity.slice(0, 25)}...`);
      return updatedTag;
    }

    return match;
  });

  fs.writeFileSync(indexPath, htmlContent, 'utf-8');
  console.log('Successfully updated index.html SRI hashes.');
}

function main() {
  copyAssets();
  updateIndexIntegrityHashes();
}

main();
