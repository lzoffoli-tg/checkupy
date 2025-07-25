"""
module allowing to use onnx models
"""

#! IMPORTS


import numpy as np
import onnx
import pandas as pd
from onnxruntime import InferenceSession
from random import randint

#! CLASSES


class OnnxModel:
    def __init__(
        self,
        model_path: str,
        input_labels: list[str],
        output_labels: list[str],
    ):
        self.model_path = model_path
        self._input_labels = input_labels
        self._output_labels = output_labels
        self.session = InferenceSession(model_path)
        self.model = onnx.load(model_path)

    @property
    def input_labels(self):
        return self._input_labels

    @property
    def output_labels(self):
        return self._output_labels

    def predict(self, data):

        # check the inputs
        target_cols = len(self._input_labels)
        wrong_cols = f"Expected input tensor with shape (N, {target_cols})"
        col_list = f"DataFrame must contain columns: {self._input_labels}"

        if isinstance(data, np.ndarray):
            if data.ndim != 2 or data.shape[1] != target_cols:
                raise ValueError(wrong_cols)
            vals = data.astype(np.float32)
            source = "ndarray"

        elif isinstance(data, pd.DataFrame):
            if not all(label in data.columns for label in self._input_labels):
                raise ValueError(col_list)
            vals = data[self._input_labels].values.astype(np.float32)
            source = "dataframe"

        elif isinstance(data, dict):
            if not all(label in data.keys() for label in self._input_labels):
                raise ValueError(col_list)
            vals = []
            for i in self._input_labels:
                if isinstance(data[i], (pd.DataFrame, pd.Series)):
                    vals.append(data[i].values.astype(np.float32).flatten())
                else:
                    arr = np.atleast_1d(data[i]).astype(np.float32).flatten()
                    vals.append(arr)
            vals = np.concatenate([i.reshape(-1, 1) for i in vals], axis=1)
            source = "dict"

        else:
            raise TypeError("Unsupported input type")

        # make the inference
        inputs = {self.session.get_inputs()[0].name: vals}
        outputs = self.session.run(None, inputs)[0]

        # adjust the outputs
        if source == "ndarray":
            return outputs

        if source == "dict":
            return {
                i: v.astype(np.float32).flatten()
                for i, v in zip(self.output_labels, outputs.T)  # type: ignore
            }

        if source == "dataframe":
            return pd.DataFrame(
                data=outputs,  # type: ignore
                index=data.index,  # type: ignore
                columns=self.output_labels,
            )

        raise TypeError("Unsupported output type")

    def __call__(self, data):
        return self.predict(data)


if __name__ == "__main__":
    onnx_model = OnnxModel(
        model_path="model2_100x2_vs_inbody.onnx",
        input_labels=[  # order is important and defined at model creation
            "height",
            "weight",
            "age",
            "sex",
            "left_arm_resistance",
            "left_arm_reactance",
            "left_leg_resistance",
            "left_leg_reactance",
            "left_body_resistance",
            "left_body_reactance",
            "right_arm_resistance",
            "right_arm_reactance",
            "right_leg_resistance",
            "right_leg_reactance",
            "right_body_resistance",
            "right_body_reactance",
        ],
        output_labels=[  # order is important and defined at model creation
            "total_body_basalmetabolicrate",
            "total_body_proteins",
            "total_body_minerals",
            "target_weight",
            "total_body_phaseangle",
            "total_body_phaseanglecorrected",
            "total_body_fatmass",
            "total_body_fatmassperc",
            "total_body_fatmassindex",
            "total_body_fatfreemass",
            "total_body_fatfreemassperc",
            "total_body_fatfreemassindex",
            "total_body_bonemineralcontentperc",
            "total_body_bonemineralcontent",
            "total_body_softleanmass",
            "total_body_softleanmassperc",
            "total_body_skeletalmusclemass",
            "total_body_skeletalmusclemassperc",
            "total_body_skeletalmusclemassindex",
            "left_arm_fatmass",
            "left_arm_fatmassperc",
            "left_arm_fatfreemass",
            "left_arm_fatfreemassperc",
            "left_leg_fatmass",
            "left_leg_fatmassperc",
            "left_leg_fatfreemass",
            "left_leg_fatfreemassperc",
            "right_arm_fatmass",
            "right_arm_fatmassperc",
            "right_arm_fatfreemass",
            "right_arm_fatfreemassperc",
            "right_leg_fatmass",
            "right_leg_fatmassperc",
            "right_leg_fatfreemass",
            "right_leg_fatfreemassperc",
            "total_trunk_fatmass",
            "total_trunk_fatmassperc",
            "total_trunk_fatfreemass",
            "total_trunk_fatfreemassperc",
            "total_body_water",
            "total_body_waterperc",
            "total_body_extracellularwater",
            "total_body_extracellularwaterperc",
            "total_body_intracellularwater",
            "total_body_intracellularwaterperc",
            "ecw_on_icw",
        ],
    )

    # get the predictions
    inputs = {i: randint(1, 100) for i in onnx_model.input_labels}
    preds = onnx_model(inputs)
    print(preds)
