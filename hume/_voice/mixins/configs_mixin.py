"""Client operations for managing EVI configurations."""

import logging
from typing import Iterator, Optional

from hume._common.client_base import ClientBase
from hume._common.utilities.paging_utilities import Paging
from hume._voice.models.configs_models import (
    ConfigResponse,
    ConfigsResponse,
    PostConfigRequest,
    PostPromptRequest,
    PromptMeta,
    PromptResponse,
    VoiceConfig,
    VoiceIdentityConfig,
)
from hume.error.hume_client_exception import HumeClientException

logger = logging.getLogger(__name__)


# pylint: disable=redefined-builtin
class ConfigsMixin(ClientBase):
    """Client operations for managing EVI configurations."""

    DEFAULT_VOICE_NAME = "ITO"

    def create_config(
        self,
        *,
        name: str,
        prompt: str,
        description: Optional[str] = None,
        voice_name: Optional[str] = DEFAULT_VOICE_NAME,
    ) -> VoiceConfig:
        """Create a new EVI config.

        Args:
            name (str): Config name.
            prompt (str): System prompt text.
            description (Optional[str]): Config description.
        """
        post_prompt_request = PostPromptRequest(name=name, version_description=description, text=prompt)
        post_prompt_body = post_prompt_request.to_json_str()
        endpoint = self._build_endpoint("evi", "prompts")
        response = self._request(endpoint, method="POST", body_json_str=post_prompt_body)
        prompt_response = PromptResponse.model_validate_json(response.text)
        prompt_meta = PromptMeta(id=prompt_response.id, version=prompt_response.version)

        post_config_request = PostConfigRequest(
            name=name,
            version_description=description,
            prompt=prompt_meta,
            voice=VoiceIdentityConfig(name=voice_name),
        )
        post_config_body = post_config_request.to_json_str()
        endpoint = self._build_endpoint("evi", "configs")
        response = self._request(endpoint, method="POST", body_json_str=post_config_body)
        config_response = ConfigResponse.model_validate_json(response.text)

        return self._config_from_response(config_response)

    def get_config(self, id: str, _version: Optional[int] = None) -> VoiceConfig:
        """Get an EVI config by its ID.

        Args:
            id (str): Config ID.
        """
        route = f"configs/{id}" if _version is None else f"configs/{id}/version/{_version}"
        endpoint = self._build_endpoint("evi", route)
        response = self._request(endpoint, method="GET")
        configs_response = ConfigsResponse.model_validate_json(response.text)
        if len(configs_response.configs_page) == 0:
            raise HumeClientException(f"Config not found with ID: {id}")

        return self._config_from_response(configs_response.configs_page[0])

    def _iter_config_versions(self, id: str) -> Iterator[VoiceConfig]:
        endpoint = self._build_endpoint("evi", f"configs/{id}")
        for page_number in range(self.PAGING_LIMIT):
            paging = Paging(page_size=self._page_size, page_number=page_number)
            response = self._request(endpoint, method="GET", paging=paging)
            configs_response = ConfigsResponse.model_validate_json(response.text)
            if len(configs_response.configs_page) == 0:
                break
            for res in configs_response.configs_page:
                yield self._config_from_response(res)

    def _config_from_response(self, config_response: ConfigResponse) -> VoiceConfig:
        prompt_response = config_response.prompt
        prompt = prompt_response.text if prompt_response is not None else None

        return VoiceConfig(
            id=config_response.id,
            name=config_response.name,
            description=config_response.version_description,
            created_on=config_response.created_on,
            modified_on=config_response.modified_on,
            prompt=prompt,
        )

    def iter_configs(self) -> Iterator[VoiceConfig]:
        """Iterate over existing EVI configs."""
        endpoint = self._build_endpoint("evi", "configs")
        for page_number in range(self.PAGING_LIMIT):
            paging = Paging(page_size=self._page_size, page_number=page_number)
            response = self._request(endpoint, method="GET", paging=paging)
            configs_response = ConfigsResponse.model_validate_json(response.text)
            if len(configs_response.configs_page) == 0:
                break
            for res in configs_response.configs_page:
                yield self._config_from_response(res)

    def delete_config(self, id: str, _version: Optional[int] = None) -> None:
        """Delete an EVI config.

        Args:
            id (str): Config ID.
        """
        route = f"configs/{id}" if _version is None else f"configs/{id}/version/{_version}"
        endpoint = self._build_endpoint("evi", route)
        self._request(endpoint, method="DELETE")
