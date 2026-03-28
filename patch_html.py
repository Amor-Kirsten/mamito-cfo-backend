import re

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

new_script = """<script>
  const LP = 500, SP = 250;
  const today = new Date().toISOString().split('T')[0];
  let sales = [];

  document.getElementById('f-date').value = today;

  function g(id) { return parseFloat(document.getElementById(id).value) || 0; }

  function updateUI() {
    const lq = parseInt(document.getElementById('l-qty').value) || 0;
    const sq = parseInt(document.getElementById('s-qty').value) || 0;
    document.getElementById('l-pay').style.display = lq ? 'block' : 'none';
    document.getElementById('s-pay').style.display = sq ? 'block' : 'none';
    document.getElementById('l-sub').textContent = 'KES ' + (lq * LP).toLocaleString();
    document.getElementById('s-sub').textContent = 'KES ' + (sq * SP).toLocaleString();
    document.getElementById('grand').textContent = 'KES ' + (lq * LP + sq * SP).toLocaleString();
  }

  ['l-qty','s-qty'].forEach(id => document.getElementById(id).addEventListener('change', updateUI));

  async function loadSales() {
    try {
      const res = await fetch('/api/sales');
      if (res.ok) {
        sales = await res.json();
        render(); stats();
      }
    } catch(err) {
      console.error(err);
      toast('⚠️ Failed to load sales');
    }
  }

  async function addSale() {
    const date = document.getElementById('f-date').value;
    const lq = parseInt(document.getElementById('l-qty').value) || 0;
    const sq = parseInt(document.getElementById('s-qty').value) || 0;
    if (!lq && !sq) return toast('⚠️ Select at least one tin');
    if (!date) return toast('⚠️ Pick a date');

    const entry = {
      date,
      large: lq ? { qty: lq, total: lq * LP, cash: g('l-cash'), mpesa: g('l-mpesa'), credit: g('l-credit') } : null,
      small: sq ? { qty: sq, total: sq * SP, cash: g('s-cash'), mpesa: g('s-mpesa'), credit: g('s-credit') } : null,
      total: lq * LP + sq * SP
    };

    try {
      const res = await fetch('/api/sales', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry)
      });
      if (res.ok) {
        await loadSales();
        reset();
        toast('✅ Sale recorded!');
      } else {
        toast('⚠️ Failed to save');
      }
    } catch(err) {
      toast('⚠️ Network error');
    }
  }

  async function del(id) {
    if (!confirm('Delete this sale?')) return;
    try {
      const res = await fetch('/api/sales/' + id, { method: 'DELETE' });
      if (res.ok) {
        await loadSales();
        toast('🗑 Removed');
      } else {
        toast('⚠️ Failed to delete');
      }
    } catch(err) {
      toast('⚠️ Network error');
    }
  }

  function fmtDate(d) {
    return new Date(d + 'T00:00:00').toLocaleDateString('en-KE', { day:'numeric', month:'short', year:'numeric' });
  }

  function payTags(o) {
    if (!o) return '';
    let t = '';
    if (o.cash > 0)   t += `<span class="tag tag-cash">Cash ${o.cash.toLocaleString()}</span> `;
    if (o.mpesa > 0)  t += `<span class="tag tag-mpesa">M-Pesa ${o.mpesa.toLocaleString()}</span> `;
    if (o.credit > 0) t += `<span class="tag tag-credit">Credit ${o.credit.toLocaleString()}</span> `;
    if (!o.cash && !o.mpesa && !o.credit) t += `<span class="tag tag-size">Unspecified</span>`;
    return t;
  }

  function render() {
    const el = document.getElementById('records');
    if (!sales.length) { el.innerHTML = '<div class="empty"><div>🥜</div>No sales recorded yet</div>'; return; }
    el.innerHTML = [...sales].reverse().map(s => `
      <div class="sale-item">
        <button class="btn-del" onclick="del(${s.id})">✕</button>
        <div class="sale-meta">
          <div class="sale-date-lbl">${fmtDate(s.date)}</div>
          <div class="sale-total">KES ${s.total.toLocaleString()}</div>
        </div>
        ${"`${s.large ? `<div class='sale-details' style='margin-bottom:5px'>\\n          <span class='tag tag-size'>800g</span>\\n          <span class='tag tag-qty'>×${s.large.qty}</span>\\n          ${payTags(s.large)}\\n        </div>` : ''}`"}
        ${"`${s.small ? `<div class='sale-details'>\\n          <span class='tag tag-size'>400g</span>\\n          <span class='tag tag-qty'>×${s.small.qty}</span>\\n          ${payTags(s.small)}\\n        </div>` : ''}`"}
      </div>
    `).join('');
  }

  function stats() {
    const tod = sales.filter(s => s.date === today);
    document.getElementById('s-rev').textContent = 'KES ' + tod.reduce((a,s) => a + s.total, 0).toLocaleString();
    document.getElementById('s-large').textContent = tod.reduce((a,s) => a + (s.large?.qty || 0), 0);
    document.getElementById('s-small').textContent = tod.reduce((a,s) => a + (s.small?.qty || 0), 0);
  }

  function reset() {
    document.getElementById('f-date').value = today;
    ['l-qty','s-qty'].forEach(id => document.getElementById(id).value = '0');
    ['l-cash','l-mpesa','l-credit','s-cash','s-mpesa','s-credit'].forEach(id => document.getElementById(id).value = '');
    updateUI();
  }

  function exportCSV() {
    if (!sales.length) return toast('No data yet');
    const rows = [['Date','Size','Qty','Total (KES)','Cash','M-Pesa','Credit']];
    [...sales].sort((a,b)=>a.id-b.id).forEach(s => {
      if (s.large) rows.push([s.date,'800g',s.large.qty,s.large.total,s.large.cash||0,s.large.mpesa||0,s.large.credit||0]);
      if (s.small) rows.push([s.date,'400g',s.small.qty,s.small.total,s.small.cash||0,s.small.mpesa||0,s.small.credit||0]);
    });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([rows.map(r=>r.join(',')).join('\\n')],{type:'text/csv'}));
    a.download = `mamito_${today}.csv`;
    a.click();
    toast('📥 Exported!');
  }
  
  function downloadPDF() {
    try {
        const date = document.getElementById('f-date').value || today;
        window.location.href = '/api/sales/report/daily?date=' + date;
        toast('📄 Downloading PDF...');
    } catch(err) {
        toast('⚠️ Failed to generate PDF');
    }
  }

  function toast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2800);
  }

  loadSales();
</script>"""

html = re.sub(r"<script>.*?</script>", new_script, html, flags=re.DOTALL)

old_buttons = '''<div class="table-head">
      <h3>Sales Records</h3>
      <button class="btn-csv" onclick="exportCSV()">⬇ CSV</button>
    </div>'''
new_buttons = '''<div class="table-head">
      <h3>Sales Records</h3>
      <div>
        <button class="btn-csv" style="background:#4CAF50;margin-right:8px;" onclick="downloadPDF()">📄 PDF</button>
        <button class="btn-csv" onclick="exportCSV()">⬇ CSV</button>
      </div>
    </div>'''
html = html.replace(old_buttons, new_buttons)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
