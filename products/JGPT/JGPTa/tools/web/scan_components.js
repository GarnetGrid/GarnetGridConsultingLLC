const fs = require('fs');
const path = require('path');

const ARGS = process.argv.slice(2);
const DIR = ARGS[0] || '.';

console.log(`🕵️  Scanning React Components in: ${DIR}`);

function walkDir(dir, callback) {
    fs.readdirSync(dir).forEach(f => {
        let dirPath = path.join(dir, f);
        let isDirectory = fs.statSync(dirPath).isDirectory();
        if (isDirectory && f !== 'node_modules' && f !== '.next') {
            walkDir(dirPath, callback);
        } else {
            callback(path.join(dir, f));
        }
    });
}

let issues = 0;

walkDir(DIR, (filePath) => {
    if (!filePath.match(/\.tsx?$/)) return;

    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');

    lines.forEach((line, i) => {
        // Rule 1: img tags without alt
        if (line.match(/<img\s/) && !line.match(/alt=["'{]/)) {
            console.log(`[A11Y] ${filePath}:${i + 1} - <img> missing 'alt' prop.`);
            issues++;
        }
        // Rule 2: button without type
        if (line.match(/<button\s/) && !line.match(/type=["'{]/)) {
            console.log(`[BEST] ${filePath}:${i + 1} - <button> missing 'type' (default is submit!).`);
            issues++;
        }
        // Rule 3: potentially dangerous HTML
        if (line.includes('dangerouslySetInnerHTML')) {
            console.log(`[SEC] ${filePath}:${i + 1} - Usage of dangerouslySetInnerHTML.`);
            issues++;
        }
        // Rule 4: console.log left in code
        if (line.match(/console\.log\(/)) {
            console.log(`[CLEAN] ${filePath}:${i + 1} - console.log() found.`);
            issues++;
        }
    });
});

if (issues === 0) {
    console.log("✨ Clean scan. No obvious issues found.");
} else {
    console.log(`\n⚠️  Found ${issues} potential issues.`);
}
