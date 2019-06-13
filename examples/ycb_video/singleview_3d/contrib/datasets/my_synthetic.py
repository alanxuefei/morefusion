import imgviz
import numpy as np

from .base import DatasetBase


class MySyntheticDataset(DatasetBase):

    def __init__(self, root_dir, class_ids=None, augmentation={}):
        super().__init__()
        self._root_dir = root_dir
        self._class_ids = class_ids
        self._augmentation = augmentation
        self._ids = self._get_ids()

    def _get_ids(self):
        ids = []
        for video_dir in sorted(self.root_dir.dirs()):
            for npz_file in sorted(video_dir.files()):
                frame_id = f'{npz_file.parent.name}/{npz_file.stem}'
                ids.append(frame_id)
        return ids

    def get_frame(self, index, bg_class=False):
        frame_id = self.ids[index]
        npz_file = self.root_dir / f'{frame_id}.npz'
        frame = np.load(npz_file)

        instance_ids = frame['instance_ids']
        class_ids = frame['class_ids']
        Ts_cad2cam = frame['Ts_cad2cam']

        cad_files = {}
        for ins_id in instance_ids:
            cad_file = npz_file.parent / f'models/{ins_id:08d}.obj'
            if cad_file.exists():
                cad_files[ins_id] = cad_file

        if not bg_class:
            keep = class_ids > 0
            instance_ids = instance_ids[keep]
            class_ids = class_ids[keep]
            Ts_cad2cam = Ts_cad2cam[keep]

        n_instance = len(instance_ids)
        assert len(class_ids) == n_instance
        assert len(Ts_cad2cam) == n_instance

        return dict(
            instance_ids=instance_ids,
            class_ids=class_ids,
            rgb=frame['rgb'],
            depth=frame['depth'],
            instance_label=frame['instance_label'],
            intrinsic_matrix=frame['intrinsic_matrix'],
            T_cam2world=frame['T_cam2world'],
            Ts_cad2cam=Ts_cad2cam,
            cad_files=cad_files,
        )


if __name__ == '__main__':
    dataset = MySyntheticDataset(
        '/home/wkentaro/data/datasets/wkentaro/objslampp/ycb_video/synthetic_data/20190402_174648.841996',  # NOQA
        class_ids=[2],
    )
    print(f'dataset_size: {len(dataset)}')

    def images():
        for i in range(0, len(dataset)):
            example = dataset[i]
            print(f"class_id: {example['class_id']}")
            print(f"pitch: {example['pitch']}")
            print(f"quaternion_true: {example['quaternion_true']}")
            print(f"translation_true: {example['translation_true']}")
            if example['class_id'] > 0:
                viz = imgviz.tile([
                    example['rgb'],
                    imgviz.depth2rgb(example['pcd'][:, :, 0]),
                    imgviz.depth2rgb(example['pcd'][:, :, 1]),
                    imgviz.depth2rgb(example['pcd'][:, :, 2]),
                ], (1, 4), border=(255, 255, 255))
                yield viz

    imgviz.io.pyglet_imshow(images())
    imgviz.io.pyglet_run()
