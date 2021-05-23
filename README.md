# AutoSave
Auto save your experiments variables.

自动保存你的变量让你的某些过程无需重复执行。

# Usage

编写代码如下：
```python
import logging
from AutoSave import AutoSave

# execute_1_notes -> execute_1_2_initial -> execute_2_1 -> execute_3_comments
class TestClass(AutoSave):
    def execute_3_comments(self):
        print(self.values.execute_1_2_initial[0])
        print(self.values.execute_1_2_initial[1])
        print(self.values.execute_2_1)
        return None

    def execute_1_notes(self):
        return None

    def execute_1_2_initial(self):
        a_str = 'asdef'
        return a_str, 10

    def execute_2_1(self):
        a_dict = {}
        for i in range(self.values.execute_1_2_initial[1]):
            a_dict[str(i)] = i + 10
        return a_dict

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)-15s %(message)s',
                        level=logging.INFO)
    t = TestClass(tmp_dir='/tmp', with_zip=True, overwrite=True)     # set direction to '\tmp'
    t.execute()                                                      # run
```

第一次运行：
```shell
2021-05-23 15:13:44,014 The execution path is ['execute_1_notes', 'execute_1_2_initial', 'execute_2_1', 'execute_3_comments'].
2021-05-23 15:14:01,509 execute_1_notes running.
2021-05-23 15:14:01,509 execute_1_2_initial running.
2021-05-23 15:14:01,511 execute_1_2_initial results is saved to file /tmp/TestClass_execute_1_2_initial.plk.zip.
2021-05-23 15:14:01,511 execute_2_1 running.
2021-05-23 15:14:01,512 execute_2_1 results is saved to file /tmp/TestClass_execute_2_1.plk.zip.
2021-05-23 15:14:01,513 execute_3_comments running.
asdef
10
{'0': 10, '1': 11, '2': 12, '3': 13, '4': 14, '5': 15, '6': 16, '7': 17, '8': 18, '9': 19}
```

第二次运行：
```shell
2021-05-23 15:18:36,323 execute_1_notes running.
2021-05-23 15:18:36,324 execute_3_comments running.
2021-05-23 15:18:36,332 execute_1_2_initial results is loaded by file /tmp/TestClass_execute_1_2_initial.plk.zip.
asdef
10
2021-05-23 15:18:36,338 execute_2_1 results is loaded by file /tmp/TestClass_execute_2_1.plk.zip.
{'0': 10, '1': 11, '2': 12, '3': 13, '4': 14, '5': 15, '6': 16, '7': 17, '8': 18, '9': 19}
```

缓存目录情况：
```shell
$ ls /tmp
TestClass_execute_1_2_initial.plk.zip    TestClass_execute_2_1.plk.zip
```
