import logging
import os
import pickle
import re
import tempfile
import zipfile

from types import SimpleNamespace
from typing import Union, Any, List, Callable, Dict


class AutoSave(object):

    class MySimpleNamespace(SimpleNamespace):
        """
        Implement: loading data from file when using it.

        Error when
        """

        def __init__(self, loading_handle: Callable[[str], Any], **kwargs: Any):
            super().__init__(**kwargs)
            self.handle = loading_handle

        def __getattribute__(self, name: str) -> Any:
            try:
                return super().__getattribute__(name)
            except AttributeError:
                one_v = self.handle(name)
                super().__setattr__(name, one_v)
                return one_v  # getattr(self, name)

    """
    Auto save & load some objs in program execution.

    class TestClass(AutoSave):
        # execute_1_notes -> execute_1_2_initial -> execute_2_1 -> execute_3_comments
        def execute_3_comments(self):
            # you can use some result calculated in pre-steps.
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
        t = TestClass(tmp_dir='..\\tmp')  # set direction to '..\\tmp'
        t.with_zip = True                 # set auto zip
        t.overwrite = True                # set auto overwrite
        t.execute()                       # run
    """

    def __init__(self, tmp_dir: str = tempfile.gettempdir(),
                 file_prefix: str = None,
                 with_zip: bool = False,
                 overwrite: bool = True,
                 lazy_loading: bool = True,
                 filename_config: Dict = None):
        """
        Auto save & load some objs in program execution.
        :param tmp_dir: tmp file saved dir.
        :param file_prefix: prefix of tmp file.
        :param with_zip: is zip?
        :param overwrite: is overwrite default?
        :param lazy_loading: is loading when used?
        :param filename_config: use a dict to set different tmp filename for each execute_xx
        """
        self._dir: str = tmp_dir
        if file_prefix is None:
            self._file_prefix: str = self.__class__.__name__
        else:
            self._file_prefix: str = file_prefix
        self.with_zip: bool = with_zip
        self.overwrite: bool = overwrite
        self.lazy_loading: bool = lazy_loading
        if self.lazy_loading:
            self.values: AutoSave.MySimpleNamespace = AutoSave.MySimpleNamespace(loading_handle=self._auto_loading_handle)
        else:
            self.values: SimpleNamespace = SimpleNamespace()
        # generate execute func list
        attr_pattern = re.compile(r'^execute_\d+(?:_\d+)*(?:_[a-zA-Z][0-9a-zA-Z]*)?(?:_[0-9a-zA-Z]*)*$')
        self.ex_list: List = []
        for attr in dir(self):
            if attr_pattern.match(attr) is not None:
                self.ex_list.append(attr)

        def name_to_list(n):
            l = []
            for s in n[8:].split('_'):
                if s.isdigit():
                    l.append(int(s))
                else:
                    break
            return l

        self.ex_list.sort(key=name_to_list)
        if filename_config is None:
            self._filename_config = {}
        else:
            self._filename_config = filename_config
        logging.info('The execution path is {}.'.format(self.ex_list))

    @staticmethod
    def load(filename: str, with_zip: bool = True) -> Union[Any, None]:
        """
        :param filename: load saved file manual.
        :param with_zip: is zip?
        :return: None.
        """
        original_filename = os.path.basename(filename)
        if with_zip and original_filename.endswith('.zip'):
            original_filename = original_filename[:-4]
        if os.path.exists(filename):
            if with_zip:
                with zipfile.ZipFile(filename, 'r', zipfile.ZIP_DEFLATED) as zf:
                    fp = zf.open(original_filename)
                    obj = pickle.loads(fp.read())
                    fp.close()
                    zf.close()
                    return obj
            else:
                with open(filename, 'rb') as fp:
                    obj = pickle.load(fp)
                    fp.close()
                    return obj
        else:
            logging.error('{} don\'t exists.'.format(filename))
            return None

    @staticmethod
    def _save(obj: Any, filename: str, with_zip: bool = True, overwrite: bool = True) -> None:
        original_filename = os.path.basename(filename)
        if with_zip and not original_filename.endswith('.zip'):
            filename += '.zip'
        elif with_zip and original_filename.endswith('.zip'):
            original_filename = original_filename[:-4]
            if len(original_filename) == 0:
                original_filename = 'tmp_filename'
        if os.path.exists(filename):
            if overwrite:
                logging.warning('File {} exists, overwrite it.'.format(filename))
            else:
                logging.error('File {} exists, don\'t overwrite it.'.format(filename))
                return
        if with_zip:
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zf:
                # try:
                zf.writestr(original_filename, pickle.dumps(obj))
                # except MemoryError:
                #     with open(original_filename, 'wb') as fp:
                #         pickle.dump(obj, fp)
                #         fp.close()
                #     zf.write(original_filename)
                zf.close()
        else:
            with open(filename, 'wb') as fp:
                pickle.dump(obj, fp)
                fp.close()

    def _auto_loading_handle(self, attr: str) -> Any:
        plk_filename = self._attr2filename(attr)
        if os.path.exists(plk_filename):
            one_return_v = AutoSave.load(plk_filename, self.with_zip)
            logging.info('{} results is loaded by file {}.'.format(attr, plk_filename))
            return one_return_v
        else:
            return None

    def _attr2filename(self, attr: str):
        plk_filename = os.path.join(self._dir, '{}_{}.plk'.format(self._file_prefix, attr))
        if self.with_zip:
            plk_filename += '.zip'
        # 优先加载给定的文件
        if attr in self._filename_config:
            if os.path.isabs(self._filename_config[attr]):
                exists_filename = self._filename_config[attr]
            else:
                exists_filename = os.path.join(self._dir, self._filename_config[attr])
            plk_filename = exists_filename

        return plk_filename

    def execute(self) -> None:
        """
        RUN
        :return: None.
        """
        for attr in self.ex_list:
            plk_filename = self._attr2filename(attr)

            if os.path.exists(plk_filename):
                if not self.lazy_loading:
                    one_return_v = AutoSave.load(plk_filename, self.with_zip)
                    setattr(self.values, attr, one_return_v)
                    logging.info('{} results is loaded by file {}.'.format(attr, plk_filename))
            else:
                one_fun = self.__getattribute__(attr)
                logging.info('{} running.'.format(attr))
                one_return_v = one_fun()
                if one_return_v is not None:
                    setattr(self.values, attr, one_return_v)
                    AutoSave._save(one_return_v, plk_filename,
                                   self.with_zip, self.overwrite)
                    logging.info('{} results is saved to file {}.'.format(attr, plk_filename))
