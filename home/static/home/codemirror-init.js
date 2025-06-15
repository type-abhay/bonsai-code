const boilerplateMap  = {
    'c': `#include <stdio.h>

int main(void) {
// Write your code here
return 0;
}
`,
    'cpp': `#include <iostream>
using namespace std;
            
int main(){ 
// Write your code here
return 0;
}`,
    'py': `print("you need boiler plate for python too?")`,
};

const modeMap = {
    'c': 'text/x-csrc',
    'cpp': 'text/x-c++src',
    'py': 'python'
};

document.addEventListener('DOMContentLoaded', function() {
    var textarea = document.querySelector('textarea.code-editor');
    var langSelect = document.getElementById('id_language');
    var defaultLang = langSelect ? langSelect.value : 'py';


    if (!textarea.value.trim()) {
        textarea.value = boilerplateMap[defaultLang] || '';
    }

    var editor = CodeMirror.fromTextArea(textarea, {
        lineNumbers: true,
        mode: modeMap[defaultLang] || 'python',
        theme: 'material-palenight'
    });

    
    var lastBoilerplate = boilerplateMap[defaultLang] || '';
    var lastLang = defaultLang;

    langSelect.addEventListener('change', function() {
        var selected = this.value;
        var newBoilerplate = boilerplateMap[selected] || '';
        var currentValue = editor.getValue();

    
        if (currentValue !== lastBoilerplate && currentValue.trim() !== '') {
            var shouldReplace = confirm(
                "Switching language will overwrite your current code in the editor. Do you want to continue?"
            );
            if (!shouldReplace) {
                this.value = lastLang;
                editor.setOption('mode', modeMap[lastLang] || 'python');
                return;
            }
        }
        editor.setValue(newBoilerplate);
        lastBoilerplate = newBoilerplate;
        lastLang = selected;
        editor.setOption('mode', modeMap[selected] || 'python');
    });

    var form = textarea.closest('form');
    if (form) {
        form.addEventListener('submit', function() {
            editor.save();
        });
    }
});
