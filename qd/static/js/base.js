function ajax_refresh(r) {
  if (r.status == 200) {
    location.href = location.href;
  } else {
    alert(r.reason);
  }
}

// 全部按钮样式统一
$(function() {
  $('body').on('click', 'button', function (e) {
    e.preventDefault();
    e.target.blur();
  })
});