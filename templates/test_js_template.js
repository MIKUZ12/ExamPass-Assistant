var Q = __QUESTIONS_PLACEHOLDER__;
var LABELS = __LABELS_PLACEHOLDER__;
var WRONG_REVIEW_PROMPT = __WRONG_REVIEW_PROMPT_PLACEHOLDER__;
var LAST_WRONG_REVIEW = '';

function pointsOf(q) {
  return q.points || q.score || 0;
}

function stripHtml(html) {
  var div = document.createElement('div');
  div.innerHTML = html || '';
  return (div.textContent || div.innerText || '').replace(/\s+/g, ' ').trim();
}

function answerText(q, value) {
  if (value === null || value === undefined || value === '') return LABELS.unanswered_label;
  var idx = parseInt(value);
  if (q.type === 'choice') {
    return String.fromCharCode(65 + idx) + '. ' + ((q.options && q.options[idx]) ? stripHtml(q.options[idx]) : '');
  }
  if (q.type === 'tf') {
    return idx === 0 ? LABELS.true_label : LABELS.false_label;
  }
  return String(value);
}

function normalizedAnswer(q) {
  if (q.type === 'tf') {
    if (q.answer === LABELS.true_label || q.answer === true || q.answer === 'true') return 0;
    if (q.answer === LABELS.false_label || q.answer === false || q.answer === 'false') return 1;
  }

  var ans = parseInt(q.answer);
  if (Number.isNaN(ans)) {
    console.error('ExamPass: Invalid answer field for question:', q.question, '| answer =', q.answer);
  }
  return ans;
}

function questionTypeLabel(type) {
  return LABELS.section[type] || type;
}

function build(){
  var container = document.getElementById('questions-container');
  if (!container) { console.error('ExamPass: questions-container not found'); return; }
  var h = '';
  var sec = '';
  var titles = LABELS.section;

  for (var i = 0; i < Q.length; i++) {
    var q = Q[i];
    var s = q.type;
    if (s !== sec) {
      sec = s;
      if (titles[s]) {
        h += '<h3>' + titles[s] + '</h3>';
      }
    }

    var qid = 'q' + i;
    h += '<div class="q-card" id="card-' + qid + '">';
    h += '<div class="q-num">' + (i+1) + '. (' + pointsOf(q) + ' ' + LABELS.points_suffix + ')</div>';
    h += '<div class="q-text">' + q.question + '</div>';

    if (q.type === 'choice') {
      var opts = q.options || [];
      for (var j = 0; j < opts.length; j++) {
        h += '<label class="option" id="opt-' + qid + '-' + j + '" onclick="sel(\'' + qid + '\',' + j + ')">';
        h += '<input type="radio" name="' + qid + '" value="' + j + '">' + String.fromCharCode(65+j) + '. ' + opts[j] + '</label>';
      }
    } else if (q.type === 'tf') {
      h += '<label class="option" id="opt-' + qid + '-0" onclick="sel(\'' + qid + '\',0)">';
      h += '<input type="radio" name="' + qid + '" value="0">' + LABELS.true_label + '</label>';
      h += '<label class="option" id="opt-' + qid + '-1" onclick="sel(\'' + qid + '\',1)">';
      h += '<input type="radio" name="' + qid + '" value="1">' + LABELS.false_label + '</label>';
    } else {
      h += '<textarea class="q-textarea" id="text-' + qid + '" placeholder="' + LABELS.placeholder + '" rows="3"></textarea>';
    }

    h += '<div class="result" id="result-' + qid + '">';
    h += '<span class="badge" id="badge-' + qid + '"></span><span id="correct-' + qid + '"></span>';
    h += '<div class="explanation">' + q.explanation + '</div>';
    if (q.pitfall) {
      h += '<div class="pitfall">' + LABELS.pitfall_prefix + q.pitfall + '</div>';
    }
    h += '</div></div>';
  }

  container.innerHTML = h;

  // Re-render MathJax for dynamically inserted formulas
  if (window.MathJax && MathJax.typesetPromise) {
    MathJax.typesetPromise([container]).catch(function(err) {
      console.error('MathJax typeset error:', err);
    });
  }
}

document.addEventListener('DOMContentLoaded', build);
if (document.readyState === 'interactive' || document.readyState === 'complete') {
  build();
}

function sel(qid, idx) {
  var prefix = 'opt-' + qid + '-';
  var all = document.querySelectorAll('[id^="' + prefix + '"]');
  for (var i = 0; i < all.length; i++) {
    all[i].classList.remove('selected');
  }
  var target = document.getElementById('opt-' + qid + '-' + idx);
  if (target) {
    target.classList.add('selected');
  }
  var radio = document.querySelector('input[name="' + qid + '"][value="' + idx + '"]');
  if (radio) {
    radio.checked = true;
  }
}

function gradeAll() {
  var score = 0;
  var wrongItems = [];
  for (var i = 0; i < Q.length; i++) {
    var q = Q[i];
    var qid = 'q' + i;
    var card = document.getElementById('card-' + qid);
    var result = document.getElementById('result-' + qid);
    var badge = document.getElementById('badge-' + qid);
    var correctEl = document.getElementById('correct-' + qid);
    if (!card || !result) continue;

    result.style.display = 'block';

    if (q.type === 'choice' || q.type === 'tf') {
      var radio = document.querySelector('input[name="' + qid + '"]:checked');
      var correctIndex = normalizedAnswer(q);
      if (radio && parseInt(radio.value) === correctIndex) {
        score += pointsOf(q);
        card.classList.add('correct');
        badge.className = 'badge badge-ok';
        badge.textContent = LABELS.correct_label;
        correctEl.innerHTML = '';
        var correctOpt = document.getElementById('opt-' + qid + '-' + correctIndex);
        if (correctOpt) correctOpt.classList.add('correct-answer');
      } else {
        card.classList.add('wrong');
        badge.className = 'badge badge-no';
        badge.textContent = LABELS.wrong_label;
        var ansText = answerText(q, correctIndex);
        correctEl.innerHTML = LABELS.answer_prefix + ansText;
        if (radio) {
          var wrongOpt = document.getElementById('opt-' + qid + '-' + radio.value);
          if (wrongOpt) wrongOpt.classList.add('wrong-answer');
        }
        var correctOpt = document.getElementById('opt-' + qid + '-' + correctIndex);
        if (correctOpt) correctOpt.classList.add('correct-answer');
        wrongItems.push({
          number: i + 1,
          type: questionTypeLabel(q.type),
          points: pointsOf(q),
          question: stripHtml(q.question),
          options: (q.options || []).map(stripHtml),
          userAnswer: answerText(q, radio ? radio.value : null),
          correctAnswer: ansText,
          explanation: stripHtml(q.explanation),
          pitfall: stripHtml(q.pitfall || ''),
          knowledgePoint: stripHtml(q.knowledge_point || q.knowledgePoint || '')
        });
      }
    } else {
      card.classList.add('correct');
      badge.className = 'badge badge-ref';
      badge.textContent = LABELS.reference_label;
    }
  }

  var sb = document.getElementById('score-box');
  if (sb) {
    sb.style.display = 'block';
    document.getElementById('score-num').textContent = score;
    sb.scrollIntoView({behavior:'smooth'});
  }

  var opts = document.querySelectorAll('.option');
  for (var i = 0; i < opts.length; i++) opts[i].style.pointerEvents = 'none';
  var tas = document.querySelectorAll('.q-textarea');
  for (var i = 0; i < tas.length; i++) tas[i].disabled = true;

  var btn = document.getElementById('grade-btn');
  if (btn) {
    btn.disabled = true;
    btn.textContent = LABELS.graded_label;
  }

  buildWrongReview(wrongItems);

  // Re-render MathJax for revealed explanations
  if (window.MathJax && MathJax.typesetPromise) {
    MathJax.typesetPromise().catch(function(err) {
      console.error('MathJax typeset error:', err);
    });
  }
}

function buildWrongReview(wrongItems) {
  var box = document.getElementById('wrong-review-box');
  if (!box) return;

  LAST_WRONG_REVIEW = renderWrongReviewMarkdown(wrongItems);

  if (!wrongItems.length) {
    box.style.display = 'block';
    box.innerHTML = '<h3>' + LABELS.wrong_review_title + '</h3><p>' + LABELS.no_wrong_questions + '</p>';
    return;
  }

  box.style.display = 'block';
  box.innerHTML = [
    '<h3>' + LABELS.wrong_review_title + '</h3>',
    '<p>' + LABELS.wrong_review_intro.replace('__COUNT__', wrongItems.length) + '</p>',
    '<div class="wrong-review-actions">',
    '<button type="button" onclick="downloadWrongReview()">' + LABELS.download_wrong_review + '</button>',
    '<button type="button" onclick="copyWrongReviewPrompt()">' + LABELS.copy_wrong_review_prompt + '</button>',
    '</div>',
    '<textarea id="wrong-review-text" readonly rows="12">' + LAST_WRONG_REVIEW.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</textarea>'
  ].join('');
}

function renderWrongReviewMarkdown(wrongItems) {
  var now = new Date().toLocaleString();
  var lines = [];

  lines.push('# ExamPass 错题分析文档');
  lines.push('');
  lines.push('- 生成时间：' + now);
  lines.push('- 错题数量：' + wrongItems.length);
  lines.push('');
  lines.push('## 给模型的错题分析 Prompt');
  lines.push('');
  if (WRONG_REVIEW_PROMPT) {
    lines.push(WRONG_REVIEW_PROMPT);
  } else {
    lines.push('请根据下面的错题记录，分析我的错因，并给出继续学习方案。要求：');
    lines.push('1. 按知识模块归类错题，不要只逐题复述答案；');
    lines.push('2. 判断每道题错在概念定义、公式推导、图表理解、条件适用、计算步骤、概念混淆还是审题；');
    lines.push('3. 对涉及公式或推导的错题，补全从前提到结论的推导链条，不能跳步；');
    lines.push('4. 对选择题，解释我选错选项为什么有迷惑性，以及正确选项和错误选项的关键边界；');
    lines.push('5. 给出需要回看课件的具体知识点、图表、公式和页/章节线索；');
    lines.push('6. 最后生成一份二次学习清单和 5 道针对这些薄弱点的进阶训练题。');
  }
  lines.push('');
  lines.push('## 错题记录');
  lines.push('');

  if (!wrongItems.length) {
    lines.push('本次没有客观题错题。');
    return lines.join('\n');
  }

  for (var i = 0; i < wrongItems.length; i++) {
    var item = wrongItems[i];
    lines.push('### 错题 ' + (i + 1) + '：第 ' + item.number + ' 题');
    lines.push('');
    lines.push('- 题型：' + item.type);
    lines.push('- 分值：' + item.points);
    lines.push('- 题干：' + item.question);
    if (item.options.length) {
      lines.push('- 选项：');
      for (var j = 0; j < item.options.length; j++) {
        lines.push('  - ' + String.fromCharCode(65 + j) + '. ' + item.options[j]);
      }
    }
    lines.push('- 我的答案：' + item.userAnswer);
    lines.push('- 正确答案：' + item.correctAnswer);
    lines.push('- 解析：' + item.explanation);
    if (item.pitfall) lines.push('- 易错点：' + item.pitfall);
    if (item.knowledgePoint) lines.push('- 对应知识点：' + item.knowledgePoint);
    lines.push('');
  }

  return lines.join('\n');
}

function downloadWrongReview() {
  if (!LAST_WRONG_REVIEW) return;
  var blob = new Blob([LAST_WRONG_REVIEW], {type: 'text/markdown;charset=utf-8'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = '错题分析文档.md';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function copyWrongReviewPrompt() {
  var text = LAST_WRONG_REVIEW || '';
  if (!text) return;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text);
  } else {
    var ta = document.getElementById('wrong-review-text');
    if (ta) {
      ta.focus();
      ta.select();
      document.execCommand('copy');
    }
  }
}
