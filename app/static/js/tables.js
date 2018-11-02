function ResetAll() {
                var cs = document.getElementsByTagName('input');
                for (i=0; i < cs.length; i++) {
                               if (cs[i].type == 'checkbox') {
                                               cs[i].checked = false;
                               }
                }
}

function ShowLevel(row,lv) {
                var tBody = row.parentNode;
                var i = row.rowIndex;
                row = tBody.rows[i]; // Попытка перейти к следующей строке
                while (row && row.className.substring(3)*1 > lv) {
                               if (row.className.substring(3)*1 == lv+1) {
                                               row.style.display = 'table-row';
                                               if ((row.querySelector('td input')) && row.querySelector('td input').checked) {
                                                               ShowLevel(row,lv+1);
                                               }
                               }
                               i+=1;
                               row = tBody.rows[i];
                }
}

function HideLevel(row,lv) {
                var i = row.rowIndex;
                var tBody = row.parentNode;
                row = tBody.rows[i]; // Попытка перейти к следующей строке
                while (row && row.className.substring(3)*1 > lv) {
                               row.style.display = 'none';
                               i+=1;
                               row = tBody.rows[i];
                }
}

function sh(el) {
                var row = el.parentNode.parentNode.parentNode;
                var lv = row.className.substring(3)*1; // Уровень строки, циферка после 'lev'
                if (row.querySelector('td input').checked) {
                               HideLevel(row,lv);
                } else {
                               ShowLevel(row,lv);
                }
}

function SwapAll(b) {
                var tbl = document.getElementsByClassName('treetable')[0];
                for (i=1; i < tbl.rows.length; i++) {
                               if (tbl.rows[i].className != 'lev1') {
                                               if (b) {tbl.rows[i].style.display = 'table-row';}
                                               else {tbl.rows[i].style.display = 'none';}
                               }

                               if (tbl.rows[i].querySelector('td input')) {tbl.rows[i].querySelector('td input').checked = b;}
                }
}
