function showConverter(type) {
  const area = document.getElementById('converter-area');
  area.innerHTML = `
    <h2>${type.replace('2', ' to ')}</h2>
    <input type="file" id="file" accept="${getAcceptType(type)}">
    <button class="glow" onclick="uploadFile('${type}')">Convert</button>
    <div id="result"></div>
  `;
}

function getAcceptType(type) {
  if (type.includes('word')) return '.doc,.docx';
  if (type.includes('jpg')) return '.jpg,.jpeg';
  if (type.includes('ppt')) return '.ppt,.pptx';
  if (type.includes('pdf')) return '.pdf';
  return '*';
}

function uploadFile(type) {
  const file = document.getElementById('file').files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  formData.append('type', type);

  fetch('/convert', {
    method: 'POST',
    body: formData
  })
  .then(response => response.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'converted_' + type + (type.includes('pdf') ? '.pdf' : (type.includes('jpg') ? '.jpg' : (type.includes('word') ? '.docx' : '.ppt')));
    a.click();
  })
  .catch(error => {
    document.getElementById('result').innerText = 'Error: ' + error;
  });
}
